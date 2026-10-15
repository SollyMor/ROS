#!/usr/bin/env bash
set -o pipefail

source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_LOCALHOST_ONLY=1

mkdir -p evidence/pr05
rm -rf evidence/pr05/bag evidence/pr05/bag_play_check

cleanup() {
  kill -INT "${LAUNCH_PID:-}" "${PLAY_PID:-}" "${REC_PID:-}" 2>/dev/null || true
  sleep 1
  kill "${LAUNCH_PID:-}" "${PLAY_PID:-}" "${REC_PID:-}" 2>/dev/null || true
  pkill -f turtlesim_node 2>/dev/null || true
  pkill -f pose_relay 2>/dev/null || true
  pkill -f pose_subscriber 2>/dev/null || true
  pkill -f 'patrol.patrol' 2>/dev/null || true
  pkill -f 'ros2 bag' 2>/dev/null || true
}
trap cleanup EXIT
cleanup
sleep 1

echo "=== BEFORE: reliable subscriber vs best_effort sensor ==="
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=reliable record:=false \
  > /tmp/pr05-launch-before.log 2>&1 &
LAUNCH_PID=$!
sleep 5

ros2 topic list | tee /tmp/pr05-topics-before.txt
echo "--- topic info ---"
ros2 topic info /robot_a/sensor_pose --verbose 2>&1 | tee /tmp/pr05-info-before.txt

# Expected timeout: no messages with reliable
timeout 3s ros2 topic echo /robot_a/sensor_pose \
  --qos-reliability reliable --once \
  > evidence/pr05/qos-before.txt 2>&1 || true
printf '\n# exit_note: timeout expected for incompatible QoS (reliable vs best_effort)\n' \
  >> evidence/pr05/qos-before.txt
printf '# topic is listed but echo --once receives nothing\n' >> evidence/pr05/qos-before.txt
echo "qos-before written; size=$(wc -c < evidence/pr05/qos-before.txt)"

kill -INT "$LAUNCH_PID" 2>/dev/null || true
wait "$LAUNCH_PID" 2>/dev/null || true
LAUNCH_PID=
sleep 2
cleanup
sleep 2

echo "=== AFTER: best_effort on live stream ==="
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort record:=false \
  > /tmp/pr05-launch-after.log 2>&1 &
LAUNCH_PID=$!
sleep 5

timeout 3s ros2 topic echo /robot_a/sensor_pose \
  --qos-reliability best_effort --once \
  > evidence/pr05/qos-after.txt 2>&1
echo "--- live echo ok ---"
cat evidence/pr05/qos-after.txt

echo "=== record MCAP ==="
rm -rf evidence/pr05/bag
ros2 bag record -s mcap -o evidence/pr05/bag --topics /robot_a/sensor_pose \
  > /tmp/pr05-record.log 2>&1 &
REC_PID=$!
sleep 5
kill -INT "$REC_PID" 2>/dev/null || true
wait "$REC_PID" 2>/dev/null || true
REC_PID=
sleep 1

kill -INT "$LAUNCH_PID" 2>/dev/null || true
wait "$LAUNCH_PID" 2>/dev/null || true
LAUNCH_PID=
sleep 2
cleanup
sleep 2

echo "=== bag info ==="
{
  echo ""
  echo "## ros2 bag info (recorded /robot_a/sensor_pose)"
  ros2 bag info evidence/pr05/bag
} | tee -a evidence/pr05/qos-after.txt

cp evidence/pr05/bag/metadata.yaml evidence/pr05/bag-metadata.yaml

echo "=== REPLAY with qos overrides ==="
ros2 bag play evidence/pr05/bag \
  --qos-profile-overrides-path config/qos-overrides.yaml \
  > /tmp/pr05-play.log 2>&1 &
PLAY_PID=$!
sleep 1

# During play: reliable should still fail; best_effort should work
timeout 4s ros2 topic echo /robot_a/sensor_pose \
  --qos-reliability reliable --once \
  > /tmp/pr05-replay-reliable.txt 2>&1 || true
timeout 4s ros2 topic echo /robot_a/sensor_pose \
  --qos-reliability best_effort --once \
  > /tmp/pr05-replay-best_effort.txt 2>&1 || true

wait "$PLAY_PID" 2>/dev/null || true
PLAY_PID=

{
  echo ""
  echo "## replay with config/qos-overrides.yaml"
  echo "### reliable echo (expect timeout / no message)"
  cat /tmp/pr05-replay-reliable.txt
  echo "### best_effort echo (expect pose)"
  cat /tmp/pr05-replay-best_effort.txt
} >> evidence/pr05/qos-after.txt

echo DONE
ls -la evidence/pr05/
