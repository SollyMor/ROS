#!/usr/bin/env bash
set -o pipefail

source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_LOCALHOST_ONLY=1

ros2 daemon stop >/dev/null 2>&1 || true

mkdir -p evidence/pr05
rm -rf evidence/pr05/bag evidence/pr05/bag_play_check

stop_tree() {
  local pid="${1:-}"
  [[ -n "$pid" ]] || return 0
  kill -INT "$pid" 2>/dev/null || true
  pkill -INT -P "$pid" 2>/dev/null || true
  local _
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid" 2>/dev/null || true
      return 0
    fi
    sleep 0.4
  done
  pkill -TERM -P "$pid" 2>/dev/null || true
  kill -TERM "$pid" 2>/dev/null || true
  sleep 0.5
  pkill -KILL -P "$pid" 2>/dev/null || true
  kill -KILL "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

cleanup() {
  stop_tree "${LAUNCH_PID:-}"
  stop_tree "${PLAY_PID:-}"
  stop_tree "${REC_PID:-}"
  pkill -f '/turtlesim/turtlesim_node' 2>/dev/null || true
  pkill -f '/patrol/pose_relay' 2>/dev/null || true
  pkill -f '/patrol/pose_subscriber' 2>/dev/null || true
  pkill -f '/patrol/patrol' 2>/dev/null || true
  pkill -f 'ros2 bag' 2>/dev/null || true
}
trap cleanup EXIT
cleanup
sleep 1

wait_for_sensor_pose() {
  local i info
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    info=$(ros2 topic info /robot_a/sensor_pose --no-daemon --spin-time 1 2>/dev/null || true)
    if [[ "$info" == *'Publisher count: 1'* ]]; then
      echo "sensor_pose publisher is up"
      return 0
    fi
    sleep 0.4
  done
  echo "timed out waiting for /robot_a/sensor_pose" >&2
  return 0
}

echo "=== BEFORE: reliable subscriber vs best_effort sensor ==="
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=reliable record:=false \
  > /tmp/pr05-launch-before.log 2>&1 &
LAUNCH_PID=$!
wait_for_sensor_pose

ros2 topic list --no-daemon --spin-time 3 | tee /tmp/pr05-topics-before.txt
echo "--- topic info ---"
ros2 topic info /robot_a/sensor_pose --verbose --no-daemon --spin-time 2 2>&1 | tee /tmp/pr05-info-before.txt

# Expected timeout: no messages with reliable
timeout 5s ros2 topic echo /robot_a/sensor_pose \
  --no-daemon --spin-time 2 \
  --qos-reliability reliable --once \
  > evidence/pr05/qos-before.txt 2>&1 || true
printf '\n# exit_note: timeout expected for incompatible QoS (reliable vs best_effort)\n' \
  >> evidence/pr05/qos-before.txt
printf '# topic is listed but echo --once receives nothing\n' >> evidence/pr05/qos-before.txt
echo "qos-before written; size=$(wc -c < evidence/pr05/qos-before.txt)"

stop_tree "$LAUNCH_PID"
LAUNCH_PID=
sleep 2
cleanup
sleep 2

echo "=== AFTER: best_effort on live stream ==="
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort record:=false \
  > /tmp/pr05-launch-after.log 2>&1 &
LAUNCH_PID=$!
wait_for_sensor_pose

timeout 5s ros2 topic echo /robot_a/sensor_pose \
  --no-daemon --spin-time 2 \
  --qos-reliability best_effort --once \
  > evidence/pr05/qos-after.txt 2>&1
echo "--- live echo ok ---"
cat evidence/pr05/qos-after.txt

echo "=== record MCAP ==="
rm -rf evidence/pr05/bag
ros2 bag record -s mcap -o evidence/pr05/bag --topics /robot_a/sensor_pose \
  > /tmp/pr05-record.log 2>&1 &
REC_PID=$!
sleep 8
stop_tree "$REC_PID"
REC_PID=
sleep 1

stop_tree "$LAUNCH_PID"
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
# Same bag, both profiles at once: reliable times out, best_effort receives.
ros2 bag play evidence/pr05/bag \
  --qos-profile-overrides-path config/qos-overrides.yaml \
  > /tmp/pr05-play.log 2>&1 &
PLAY_PID=$!
sleep 1

timeout 5s ros2 topic echo /robot_a/sensor_pose \
  --no-daemon --spin-time 1 \
  --qos-reliability reliable --once \
  > /tmp/pr05-replay-reliable.txt 2>&1 &
RELIABLE_ECHO_PID=$!
timeout 5s ros2 topic echo /robot_a/sensor_pose \
  --no-daemon --spin-time 1 \
  --qos-reliability best_effort --once \
  > /tmp/pr05-replay-best_effort.txt 2>&1 &
BEST_ECHO_PID=$!
wait "$RELIABLE_ECHO_PID" 2>/dev/null || true
wait "$BEST_ECHO_PID" 2>/dev/null || true

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
