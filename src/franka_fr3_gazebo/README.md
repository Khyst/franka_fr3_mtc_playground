## panda_world.sdf

Panda/FR3 로봇 팔 시뮬레이션을 위한 Gazebo 환경 정의 파일

### 1. 시뮬레이션 시스템 (Physics & Plugins)

- **Physics**
	- `max_step_size`: 0.001s (1ms) 단위로 물리 연산
	- `real_time_factor`: 1.0 (실제 시간과 시뮬레이션 시간 동기화)

- **필수 플러그인**
	- Physics: 물리 법칙 적용을 위한 플러그인
	- UserCommands: 사용자 명령 처리를 위한 플러그인
	- SceneBroadcaster: 시뮬레이션 상태 렌더링 방송을 위한 플러그인 (현재 매니퓰레이터 혹은 물체의 상태를 브로드 캐스팅)

### 2. 사용자 인터페이스 (GUI)

- 3D View: ogre2 엔진, 카메라 초기 위치 (2, 2, 2)
- World Control: 재생/일시정지 버튼 (기본: 일시정지)
- World Stats: 시뮬레이션/실제 시간 정보 우측 하단 표시

### 3. 환경 및 조명 (Environment & Light)

- Sun: 직사광선(Directional Light), 그림자 생성 활성화
- Ground Plane: 무한 평면 지면, 모델 추락 방지

### 4. 배치된 모델 정보 (Included Models)

[Gazebo Fuel](https://app.gazebosim.org/fuel/models) 외부 저장소에서 모델을 불러와 아래와 같이 배치


| 모델 이름         | 위치 (x, y, z)      | 특징                       |
|-------------------|---------------------|----------------------------|
| table1            | (0, 0, 0)           | 기본 작업대                |
| table2            | (0.794, 0, 0)       | 추가 작업대                |
| Bumblebee Figure  | (0.75, -0.25, 1.025)| 테이블 위 좌측 피규어       |
| Coffee Mug        | (0.75, 0, 1.025)    | 테이블 중앙 머그컵          |
| Thor Figure       | (0.75, 0.25, 1.025) | 테이블 위 우측 피규어       |


### 5. 배치된 매니퓰레이터 정보 (Included Franka FR3 Manipulator with Gripper)


| 매니퓰레이터 이름         | 위치 (x, y, z)      | 특징                       |
|-------------------|---------------------|----------------------------|
| panda            | (0.2, 0, 1.025)           | Franka 제공 FR3 매니퓰레이터   |