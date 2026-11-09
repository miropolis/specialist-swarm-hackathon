import hashlib
import os

from anthropic.lib import files_from_dir

from agents import COORDINATOR_SYSTEM, SPECIALISTS
from common import BASE_DIR, STATE_DIR, make_client, read_state, write_state


def main() -> None:
    client = make_client()
    model = os.environ.get("EMERGENCY_MODEL", "claude-haiku-4-5-20251001")
    state = read_state("deployment") if (STATE_DIR / "deployment.json").exists() else {}
    skill_dir = BASE_DIR / "skills" / "emergency-research"
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(skill_dir).as_posix().encode())
            digest.update(path.read_bytes())
    fingerprint = digest.hexdigest()
    if not state.get("skill_id"):
        skill = client.beta.skills.create(
            display_name="Emergency Handling Demo Research",
            files=files_from_dir(str(skill_dir)),
        )
        state["skill_id"] = skill.id
        state["skill_fingerprint"] = fingerprint
        write_state("deployment", state)
    elif state.get("skill_fingerprint") != fingerprint:
        client.beta.skills.versions.create(
            state["skill_id"], files=files_from_dir(str(skill_dir))
        )
        state["skill_fingerprint"] = fingerprint
        write_state("deployment", state)

    specialist_ids = state.setdefault("specialists", {})
    for key, spec in SPECIALISTS.items():
        arguments = {
            "name": spec["name"],
            "model": model,
            "system": spec["system"],
            "tools": [{"type": "agent_toolset_20260401"}],
            "skills": ([{"type": "custom", "skill_id": state["skill_id"], "version": "latest"}]
                       if key == "researcher" else []),
            "metadata": {"project": "emergency-handling", "role": key},
        }
        if key in specialist_ids:
            current = client.beta.agents.retrieve(specialist_ids[key])
            agent = client.beta.agents.update(current.id, version=current.version, **arguments)
        else:
            agent = client.beta.agents.create(**arguments)
        specialist_ids[key] = agent.id
        write_state("deployment", state)
        print(f"Ready: {spec['name']} ({agent.id})", flush=True)

    coordinator_args = {
        "name": "Emergency Response Coordinator",
        "model": {
            "id": os.environ.get("EMERGENCY_COORDINATOR_MODEL", "claude-sonnet-4-6"),
            "effort": {"type": "low"},
        },
        "system": COORDINATOR_SYSTEM,
        "tools": [{"type": "agent_toolset_20260401"}],
        "multiagent": {
            "type": "coordinator",
            "agents": [{"type": "agent", "id": agent_id} for agent_id in specialist_ids.values()],
        },
        "metadata": {"project": "emergency-handling", "role": "coordinator"},
    }
    if state.get("coordinator_id"):
        current = client.beta.agents.retrieve(state["coordinator_id"])
        coordinator = client.beta.agents.update(current.id, version=current.version, **coordinator_args)
    else:
        coordinator = client.beta.agents.create(**coordinator_args)
    state["coordinator_id"] = coordinator.id
    write_state("deployment", state)

    if not state.get("environment_id"):
        environment = client.beta.environments.create(
            name="emergency-handling-demo",
            config={"type": "cloud", "networking": {"type": "unrestricted"}},
        )
        state["environment_id"] = environment.id
        write_state("deployment", state)
    print("Setup complete. Run: python emergency-handling/run_emergency.py")


if __name__ == "__main__":
    main()