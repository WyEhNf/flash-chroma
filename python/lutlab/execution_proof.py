"""核对原生执行内核；旧记录只允许无歧义的显式命令证据。"""


def validate_native_kernel(execution, declared, backend="cpu"):
    if execution.get("backend") != "cpu" or backend != "cpu":
        raise ValueError("原生执行的内核/后端与登记证据不一致")
    command = execution.get("command", [])
    requested = None
    if "-k" in command:
        position = command.index("-k") + 1
        if command.count("-k") != 1 or position >= len(command):
            raise ValueError("原生命令的内核参数缺失或重复")
        requested = command[position]
    # 历史 cube 没有 JSON 输出，只能接受明确指定且成功执行的非 auto 命令。
    actual = execution["kernel"] if "kernel" in execution else requested
    if (not isinstance(actual, str) or not actual or actual in ("auto", "tetra_auto")
            or actual != declared or requested not in (None, "auto", actual)):
        raise ValueError("原生执行的内核/后端与登记证据不一致")
    return "native_reported_kernel" if "kernel" in execution else "legacy_explicit_command"
