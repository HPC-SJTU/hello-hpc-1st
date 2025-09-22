project(RopeSimulator)
cmake_minimum_required(VERSION 3.15)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")

include_directories(.)

add_executable(${PROJECT_NAME}
    main.cpp
    acceleration.cpp
    calGF.cpp
    LoadFNS.cpp
    LoadPolyhedron.cpp
    LoadSHPara.cpp
    MatrixOperations.cpp
    OdeEuler.cpp
    SurfacePoints.cpp
    initialize.cpp
)