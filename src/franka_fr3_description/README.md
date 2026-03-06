## Franka FR3 Robot Kinematics: Coordinate Transformation Summary

### 1. Joint (조인트 정보)
---
#### 1) Translation (위치 변환)

각 부모 프레임으로부터 자식 프레임이 떨어진 거리(m)

| 변환 구간 (Parent → Child) | x (m) | y (m) | z (m) | world 기준 (x, y, z) | 비고 |
| --- | --- | --- | --- | --- | --- |
| world → link0 | 0.0 | 0.0 | 0.0 | (0.0, 0.0, 0.0) | 월드 원점 고정 |
| link0 → link1 | 0.0 | 0.0 | 0.333 | (0.0, 0.0, 0.333) | 베이스 높이 |
| link1 → link3 | 0.0 | -0.316 | 0.0 | (0.0, -0.316, 0.333) | 상완(Upper Arm) 길이 |
| link3 → link4 | 0.0825 | 0.0 | 0.0 | (0.0825, -0.316, 0.333) | 링크 오프셋 |
| link4 → link5 | -0.0825 | 0.384 | 0.0 | (0.0, 0.068, 0.333) | 하완(Forearm) 길이 |
| link5 → link7 | 0.088 | 0.0 | 0.0 | (0.088, 0.068, 0.333) | 손목 구간 길이 |
| link7 → link8 | 0.0 | 0.0 | 0.107 | (0.088, 0.068, 0.44) | 플랜지 끝단 위치 |

#### 2) Rotation (회전 변환)

로봇의 정적(Static) 설계에 따른 고유 회전 값 (동적 관절 각도는 제외)

- **fr3_link8 (Flange) 고유 회전**
	- 그리퍼 장착을 위해 $z$축 기준 $-45^\circ$ ($-0.785\text{ rad}$) 회전
	- 쿼터니언: $x: 0, y: 0, z: -0.3826, w: 0.9238$
- **관절 기본 정렬**
	- 대부분의 링크는 초기 상태에서 부모 프레임과 축이 평행
	- link1↔link2 구간 등 일부는 설계상 $\pm1.57\text{ rad}$ 비틀림 존재

#### 3) Axis (회전 축 정보)

각 관절이 회전하는 기준 축과 방향 규칙

- **회전 축 방향**: FR3는 표준 로봇 좌표계(Right-Hand Rule)를 따름
- **축 의미**
	- $Z$축 (Blue): 관절 회전 중심축 (Revolute Axis)
	- $X$축 (Red): 링크 전방 방향
	- $Y$축 (Green): 오른손 법칙에 따른 측면 방향
- **특이 사항**
	- 홀수 관절(fr3_link1, fr3_link3, fr3_link5, fr3_link7)은 수직/수평 회전을 담당
	- 짝수 관절은 **굴곡(Bending)** 중심 동작을 담당

### 2. End-Effector (그리퍼 정보)
---
#### 1) Translation (위치 변환)

| 변환 구간 (Parent → Child) | x (m) | y (m) | z (m) | 비고 |
| --- | --- | --- | --- | --- |
| link7 → link8 | 0.0 | 0.0 | 0.107 | 플랜지(Flange) 끝단 위치 |
| hand → hand_tcp | 0.0 | 0.0 | 0.1034 | 최종 작업점(TCP) 오프셋 |
| hand → leftfinger | 0.0 | 0.0 | 0.0584 | 왼쪽 손가락 기부(Base) 높이 |
| hand → rightfinger | 0.0 | 0.0 | 0.0584 | 오른쪽 손가락 기부(Base) 높이 |

#### 2) Rotation (회전 변환)

- **Gripper Mounting (link8 → hand)**
	- 설계 각도: $Z$축 기준 $-45^\circ$ ($-0.785\text{ rad}$) 회전
	- Quaternion: $x: 0, y: 0, z: -0.3826, w: 0.9238$
	- 의미: 로봇 팔 마지막 링크와 그리퍼 방향 정렬을 위한 고정 오프셋
- **hand → hand_tcp**
	- Rotation: 없음 ($w: 1.0$)
	- 그리퍼 정면 방향과 작업 방향이 일치

#### 3) Axis (축 및 가동 정보)

- **작업축 ($Z$-Axis)**: hand_tcp의 $Z$축(Blue) 방향이 로봇이 물체에 접근하는 정면 방향
- **파지축 ($Y$-Axis)**: leftfinger와 rightfinger 사이의 $Y$축(Green) 거리가 변하며 물체를 잡거나 놓음
	- $y > 0$: 손가락이 벌어지는 방향
	- $y \approx 0$: 손가락이 완전히 닫힌 상태

### 참고 (For Developer)
- 단위: 모든 수치는 SI 단위(meters, radians)