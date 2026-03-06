cmake_minimum_required(VERSION 3.8)
project(franka_fr3_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

install(DIRECTORY worlds models
  DESTINATION share/${PROJECT_NAME}/
)

# Register environment hooks so GZ_SIM_RESOURCE_PATH / GAZEBO_MODEL_PATH are
# set correctly when the workspace is sourced.
ament_environment_hooks(
  "${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/franka_fr3_gazebo.dsv"
  "${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/franka_fr3_gazebo.sh.in"
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
