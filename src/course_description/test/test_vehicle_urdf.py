"""Structural checks for the Ackermann Xacro description."""

from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import pytest

XACRO = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'

SENSOR_XYZ = (0.28, 0.0, 0.38)


def expand_urdf() -> str:
    """Run xacro and return the URDF text."""
    result = subprocess.run(
        ['xacro', str(XACRO)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def joint_map(root: ET.Element) -> dict[str, ET.Element]:
    return {joint.attrib['name']: joint for joint in root.findall('joint')}


def origin_xyz(joint: ET.Element) -> list[float]:
    raw = joint.find('origin').attrib.get('xyz', '0 0 0')
    return [float(part) for part in raw.split()]


@pytest.fixture(scope='module')
def urdf_root() -> ET.Element:
    return ET.fromstring(expand_urdf())


def test_xacro_file_exists():
    assert XACRO.is_file()


def test_check_urdf_accepts_tree(tmp_path: Path):
    urdf_path = tmp_path / 'vehicle.urdf'
    urdf_path.write_text(expand_urdf(), encoding='utf-8')
    result = subprocess.run(
        ['check_urdf', str(urdf_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Successfully Parsed XML' in result.stdout


def test_no_gazebo_plugins(urdf_root: ET.Element):
    text = ET.tostring(urdf_root, encoding='unicode')
    assert '<gazebo' not in text
    assert '<plugin' not in text


def test_lidar_parent_is_base_link(urdf_root: ET.Element):
    """Lidar is fixed to the chassis, not to the camera."""
    joint = joint_map(urdf_root)['lidar_joint']
    assert joint.attrib['type'] == 'fixed'
    assert joint.find('parent').attrib['link'] == 'base_link'
    assert joint.find('child').attrib['link'] == 'lidar_link'
    assert origin_xyz(joint) == pytest.approx(SENSOR_XYZ)


def test_camera_and_imu_parents(urdf_root: ET.Element):
    joints = joint_map(urdf_root)
    for name in ('camera_joint', 'imu_joint'):
        joint = joints[name]
        assert joint.find('parent').attrib['link'] == 'base_link'
        assert origin_xyz(joint) == pytest.approx(SENSOR_XYZ)
    optical = joints['camera_optical_joint']
    assert optical.find('parent').attrib['link'] == 'camera_link'
    assert optical.find('child').attrib['link'] == 'camera_optical_frame'


def test_track_and_wheel_base(urdf_root: ET.Element):
    joints = joint_map(urdf_root)
    assert origin_xyz(joints['front_left_steering_joint']) == pytest.approx([0.4, 0.31, 0.0])
    assert origin_xyz(joints['front_right_steering_joint']) == pytest.approx([0.4, -0.31, 0.0])
    assert origin_xyz(joints['rear_left_wheel_joint']) == pytest.approx([-0.4, 0.31, 0.0])
    assert origin_xyz(joints['rear_right_wheel_joint']) == pytest.approx([-0.4, -0.31, 0.0])
    assert joints['front_left_wheel_joint'].find('parent').attrib['link'] == 'front_left_knuckle'


def test_visual_and_collision_are_separate(urdf_root: ET.Element):
    base = next(link for link in urdf_root.findall('link') if link.attrib['name'] == 'base_link')
    assert base.find('visual/geometry/box').attrib['size'] == '1.05 0.52 0.22'
    assert base.find('collision/geometry/box').attrib['size'] == '1.05 0.52 0.22'
    wheel = next(link for link in urdf_root.findall('link') if link.attrib['name'] == 'rear_left_wheel')
    assert float(wheel.find('visual/geometry/cylinder').attrib['radius']) == pytest.approx(0.12)
    assert float(wheel.find('collision/geometry/cylinder').attrib['radius']) == pytest.approx(0.12)
    assert wheel.find('visual') is not wheel.find('collision')


def test_tree_is_connected_and_acyclic(urdf_root: ET.Element):
    parents = {}
    for joint in urdf_root.findall('joint'):
        child = joint.find('child').attrib['link']
        parent = joint.find('parent').attrib['link']
        assert child not in parents, child
        parents[child] = parent
    links = {link.attrib['name'] for link in urdf_root.findall('link')}
    assert 'base_link' in links
    assert 'base_link' not in parents
    for link in links:
        seen = set()
        current = link
        while current != 'base_link':
            assert current not in seen
            seen.add(current)
            assert current in parents
            current = parents[current]


def test_inertias_are_physical(urdf_root: ET.Element):
    for link in urdf_root.findall('link'):
        inertia = link.find('inertial/inertia')
        if inertia is None:
            continue
        ixx = float(inertia.attrib['ixx'])
        iyy = float(inertia.attrib['iyy'])
        izz = float(inertia.attrib['izz'])
        assert ixx > 0 and iyy > 0 and izz > 0
        assert ixx + iyy >= izz
        assert ixx + izz >= iyy
        assert iyy + izz >= ixx
        assert float(link.find('inertial/mass').attrib['value']) > 0
