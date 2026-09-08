# Start with the conversation you need

Interpersonal Strategist is an experimental thinking and practice aid. It does
not know another person's private motives or validate a relationship score.
The current package is `0.13.0-alpha.1`; target-host and human qualification are
still pending. See [capabilities](release/host-capabilities.json).

## Four starting points

| Your task | Example invocation |
|---|---|
| Prepare a conversation | `$interpersonal-strategist Help me ask my manager which task to deprioritize. The deadline is Friday.` |
| Think through a situation | `$interpersonal-strategist My friend cancelled twice. Help me decide what to do, without guessing why.` |
| Practice a response | `$interpersonal-strategist Rehearse saying no to another unpaid request. One turn at a time.` |
| Review what happened | `$interpersonal-strategist I tried the request. Here is what they said. What changes now?` |

Include the decision, a concrete event or exact words, and a constraint that
could change the next move. Use aliases and the minimum excerpt. Do not upload
whole chat histories, confidential files, or intimate material merely to add
context. The skill may ask one question and wait; it should not interrogate you
about information that cannot change the decision.

`Quick mode` requests a bounded answer now. `Grill me` requests a candid
interview, not an accusation or a personality assessment. `Stop` ends the current
interview or simulation. `Current read` asks for advice using the facts so far.
A simple task can have a one-line answer.

The useful result is a shared read, one next move, wording you can stand behind,
and a review/stop condition where needed. A recommendation can be to pause,
maintain a boundary, ask a clarifying question, or take no further action.

## Control your information

Session-only is the default. `Memory off` prohibits skill-initiated record
writes; it does not delete the host's chat history or provider logs. No host
adapter is qualified in this release. A copyable case card is available only
when requested; copying it elsewhere is your action and may create another copy.

Inspect, correct, expire, export, or delete persistent case records only through
an adapter that has demonstrated the specific operation. Never accept “saved”
or “deleted” without a host receipt. An evidence table is the default decision
aid. Request a numerical calculation only for a named decision and explicit
weights; incomplete or gated decisions have no overall score.

## Installation and a first check

Build with `python3 scripts/package.py`; the ZIP is created in `dist/` alongside
a checksum and manifest. Use the supported Skills installation interface for
your host; see the [README installation section](README.md#installation).
Review the files before installation. A local layout smoke test checks archive
structure, not actual model loading or runtime behavior.

After installing, explicitly invoke the skill on a synthetic low-stakes case.
Check that it can find the relevant reference, honor quick mode, ask and wait
when needed, and stop. Record the host/model/version and tool-read evidence
before claiming compatibility. No account credentials or API keys are bundled.

## 中文开始方式

先说清你要做什么，不必先填人物档案或打分：

- 准备沟通：`$interpersonal-strategist 帮我和主管讨论任务优先级。周五前只能完成一项。`
- 梳理局面：`$interpersonal-strategist 朋友连续取消两次见面。帮我决定下一步，不要猜测动机。`
- 练习回应：`$interpersonal-strategist 陪我练习拒绝额外的无偿工作，一次只演一轮。`
- 复盘结果：`$interpersonal-strategist 我按计划提出了请求，对方这样回复。现在应如何调整？`

可说“快速模式”“先问我”“当前判断”或“停止”。默认只用本次对话，不保存
人物档案。需要背景时，只提供足以改变决策的信息；使用代称，不必上传完整聊天。
“关闭记忆”不等于删除平台记录。演练是假设场景，不是对真实人物的预测。
这些中文示例尚未经过发布门槛要求的两位独立流利评审。

## Report a problem without exposing the people involved

Use [SECURITY.md](SECURITY.md) for privacy or harmful-advice concerns. For an
ordinary defect, report version, host/model, a synthetic reproduction, expected
behavior, and actual behavior. Do not post identifiable situations in public
issues. Stop using an affected feature when its behavior violates a boundary.
