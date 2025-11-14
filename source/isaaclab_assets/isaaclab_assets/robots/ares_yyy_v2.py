# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for Unitree robots.

The following configurations are available:

* :obj:`ARES_YYY2_CFG`: ARES YYY v2 dog
"""

import isaaclab.sim as sim_utils
from isaaclab.actuators import DCMotorCfg, ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
# from isaaclab.utils.assets import ISAACLAB_NUCLEUS_DIR

ARES_YYY2_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path="/home/ares/dog_ws/DOGV2.16.SLDASM/DOGV216.usd",
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False, solver_position_iteration_count=4, solver_velocity_iteration_count=0
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.3),
        joint_pos={".*": 0.0},
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.9,
    actuators={
        "hip_joints": DCMotorCfg(
            joint_names_expr=[".*_HipA_joint", ".*_HipF_joint"],
            effort_limit=17.0,
            saturation_effort=17.0,
            peak_torque_speed=8.4,
            velocity_limit=22.0,
            stiffness=25.0,
            damping=0.5,
            friction=0.0,
        ),
        "knee_joints": DCMotorCfg(
            joint_names_expr=[".*_Knee_joint"],
            effort_limit=25.0,
            saturation_effort=25.0,
            peak_torque_speed=3.7,
            velocity_limit=13.0,
            stiffness=25.0,
            damping=0.5,
            friction=0.0,
        ),
        "wheels": ImplicitActuatorCfg(
            joint_names_expr=[".*_Wheel_joint"],
            effort_limit_sim=2.4,
            velocity_limit_sim=50.0,
            stiffness=0.0,
            damping=0.5,
            friction=0.0,
        ),
    },
)
"""Configuration of ARES YYY v2 dog using DC-Motor actuator model."""
