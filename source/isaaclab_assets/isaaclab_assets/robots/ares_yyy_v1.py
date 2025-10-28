# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for Unitree robots.

The following configurations are available:

* :obj:`ARES_YYY1_CFG`: ARES YYY v1 dog
"""

import isaaclab.sim as sim_utils
from isaaclab.actuators import DCMotorCfg
from isaaclab.assets.articulation import ArticulationCfg
# from isaaclab.utils.assets import ISAACLAB_NUCLEUS_DIR

ARES_YYY1_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path="/mnt/hdd/homes/ares/dog_ws/dogv121.sldasm/usd/dogV121.SLDASM.usd",
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
        "base_legs": DCMotorCfg(
            joint_names_expr=[".*_HipA_joint", ".*_HipF_joint"],
            effort_limit=17,
            saturation_effort=17,
                '.*HipF_joint': 17,
                '.*Knee_joint': 34,
            },
            saturation_effort={
                '.*HipA_joint': 17,
                '.*HipF_joint': 17,
                '.*Knee_joint': 34,
            },
            peak_torque_speed={
                '.*HipA_joint': 8.4,
                '.*HipF_joint': 8.4,
                '.*Knee_joint': 4.1,
            },
            velocity_limit={
                '.*HipA_joint': 22.0,
                '.*HipF_joint': 22.0,
                '.*Knee_joint': 11.0,
            },
            stiffness=25.0,
            damping=0.5,
            friction=0.0,
        ),
    },
)
"""Configuration of ARES YYY v1 dog using DC-Motor actuator model."""
