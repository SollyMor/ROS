cmake_minimum_required(VERSION 3.8)
project(course_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch rviz urdf
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_vehicle_urdf test/test_vehicle_urdf.py)
  find_package(launch_testing_ament_cmake REQUIRED)
  add_launch_test(test/test_display_launch.py)
endif()

ament_package()
