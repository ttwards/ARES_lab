# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from isaaclab.utils import configclass
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg, RewardsCfg
import isaaclab.envs.mdp as base_mdp
import isaaclab_tasks.manager_based.locomotion.velocity.mdp as mdp

##
# Pre-defined configs
##
from isaaclab_assets.robots.ares_yyy_v2 import ARES_YYY2_CFG  # isort: skip


@configclass
class YYYv2ActionsCfg:
    """Action specifications with separate position and velocity control."""

    # Position control for leg joints (excluding wheels)
    joint_pos = base_mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=[".*_HipA_joint", ".*_HipF_joint", ".*_Knee_joint"],
        scale=0.25,
        use_default_offset=True
    )
    # Velocity control for wheel joints
    wheel_vel = base_mdp.JointVelocityActionCfg(
        asset_name="robot",
        joint_names=[".*_Wheel_joint"],
        scale=20.0,
        use_default_offset=True
    )


@configclass
class YYYv2ObservationsCfg:
    """Observation specifications with separate observations for legs and wheels."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Custom observations for policy group."""

        # Base observations
        base_lin_vel = ObsTerm(func=base_mdp.base_lin_vel, noise=Unoise(n_min=-0.1, n_max=0.1))
        base_ang_vel = ObsTerm(func=base_mdp.base_ang_vel, noise=Unoise(n_min=-0.2, n_max=0.2))
        projected_gravity = ObsTerm(
            func=base_mdp.projected_gravity,
            noise=Unoise(n_min=-0.05, n_max=0.05),
        )
        velocity_commands = ObsTerm(func=base_mdp.generated_commands, params={"command_name": "base_velocity"})

        # Leg joint position (excluding wheels)
        joint_pos = ObsTerm(
            func=base_mdp.joint_pos_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_HipA_joint", ".*_HipF_joint", ".*_Knee_joint"])},
            noise=Unoise(n_min=-0.01, n_max=0.01)
        )
        # Leg joint velocity (excluding wheels)
        joint_vel = ObsTerm(
            func=base_mdp.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_HipA_joint", ".*_HipF_joint", ".*_Knee_joint", ".*Wheel_joint"])},
            noise=Unoise(n_min=-0.25, n_max=0.25)
        )

        actions = ObsTerm(func=base_mdp.last_action)
        height_scan = ObsTerm(
            func=base_mdp.height_scan,
            params={"sensor_cfg": SceneEntityCfg("height_scanner")},
            noise=Unoise(n_min=-0.1, n_max=0.1),
            clip=(-1.0, 1.0),
        )

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class YYYv2RewardsCfg(RewardsCfg):
    """Reward terms for the MDP."""

    # joint_vel_wheel_l2 = RewTerm(
    #     func=mdp.joint_vel_l2, weight=0.0, params={"asset_cfg": SceneEntityCfg("robot", joint_names="")}
    # )

    # joint_acc_wheel_l2 = RewTerm(
    #     func=mdp.joint_acc_l2, weight=0.0, params={"asset_cfg": SceneEntityCfg("robot", joint_names="")}
    # )

    # joint_torques_wheel_l2 = RewTerm(
    #     func=mdp.joint_torques_l2, weight=0.0, params={"asset_cfg": SceneEntityCfg("robot", joint_names="")}
    # )


@configclass
class AresYYYv2RoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    # Override actions with custom configuration
    actions: YYYv2ActionsCfg = YYYv2ActionsCfg()
    # Override observations with custom configuration
    observations: YYYv2ObservationsCfg = YYYv2ObservationsCfg()

    rewards: YYYv2RewardsCfg = YYYv2RewardsCfg()

    base_link_name = "base_link"
    foot_link_name = ".*_Wheel_link"

    leg_joint_names = [".*_HipA_joint", ".*_HipF_joint", ".*_Knee_joint"]
    wheel_joint_names = [".*_Wheel_joint"]
    joint_names = leg_joint_names + wheel_joint_names

    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        self.scene.robot = ARES_YYY2_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/" + self.base_link_name
        # scale down the terrains because the robot is small
        self.scene.terrain.terrain_generator.sub_terrains["boxes"].grid_height_range = (0.025, 0.1)
        self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_range = (0.01, 0.06)
        self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_step = 0.01
        # self.scene.contact_forces.prim_path = "{ENV_REGEX_NS}/Robot/.*"

        # Adjust action scales for specific joints
        self.actions.joint_pos.scale = {".*": 0.125}

        # event
        self.events.push_robot = None
        self.events.add_base_mass.params["mass_distribution_params"] = (-1.0, 3.0)
        self.events.add_base_mass.params["asset_cfg"].body_names = "base_link"
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "base_link"
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)
        self.events.reset_base.params = {
            "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
        }
        self.events.base_com = None

        # rewards
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = self.foot_link_name
        self.rewards.feet_air_time.weight = 0.01

        self.rewards.undesired_contacts.params["sensor_cfg"].body_names = [f"^(?!.*{self.foot_link_name}).*"]
        self.rewards.undesired_contacts.weight = -1.8

        self.rewards.dof_torques_l2.weight = -0.0002
        self.rewards.track_lin_vel_xy_exp.weight = 1.5
        self.rewards.track_ang_vel_z_exp.weight = 0.75
        self.rewards.dof_acc_l2.weight = -2.5e-7

        self.rewards.flat_orientation_l2.weight = -2.

        # terminations
        self.terminations.base_contact = None


@configclass
class AresYYYv2RoughEnvCfg_PLAY(AresYYYv2RoughEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # make a smaller scene for play
        self.scene.num_envs = 100
        self.scene.env_spacing = 2.5
        # spawn the robot randomly in the grid (instead of their terrain levels)
        self.scene.terrain.max_init_terrain_level = None
        # reduce the number of terrains to save memory
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.num_rows = 5
            self.scene.terrain.terrain_generator.num_cols = 5
            self.scene.terrain.terrain_generator.curriculum = False

        # disable randomization for play
        self.observations.policy.enable_corruption = False
        # remove random pushing event
        self.events.base_external_force_torque = None
        self.events.push_robot = None
