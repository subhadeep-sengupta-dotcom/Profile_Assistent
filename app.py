"""Hugging Face Spaces-ready Gradio interface for Subhadeep's profile."""

import gradio as gr

from graph import run_profile_graph

CSS = """
:root {
    --ink: #183d35;
    --muted: #687b75;
    --line: #dce5df;
    --paper: #eef3ef;
    --coral: #f1a17e;
    --lime: #d9e89d;
    --green: #215c4a;
}
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; overflow: hidden; }
body, .gradio-container { background: var(--paper) !important; color: var(--ink); }
.gradio-container {
    width: 100%; height: 100svh !important; min-height: 0 !important;
    max-width: none !important; margin: 0 auto !important;
    padding: 14px clamp(14px, 4vw, 58px) !important; overflow: hidden !important;
}
.gradio-container > main.app { width: 100%; height: 100%; min-height: 0; max-width: none; margin: 0; padding: 0 !important; }
.gradio-container > main.app > .wrap { width: 100%; height: 100%; min-height: 0; max-width: none; margin: 0; padding: 0 !important; }
.gradio-container > main.app > .wrap > .contain { width: 100%; height: 100%; min-height: 0; max-width: none; margin: 0; padding: 0; }
.gradio-container > main.app > .wrap > .contain > .column { height: 100%; flex: 1 1 0; min-height: 0; max-width: 1160px; margin: 0 auto; }
#app-shell { height: 100%; min-height: 0; gap: 10px; }
.profile-header {
    position: relative; display: grid; grid-template-columns: 1fr auto; align-items: center;
    column-gap: 24px; padding: 19px 26px; border-radius: 13px; overflow: hidden;
    background: linear-gradient(112deg, #163c34 0%, #205b4b 72%, #397563 100%);
    color: #f5f3e9; box-shadow: 0 10px 28px rgba(25, 66, 53, .13);
}
.header-copy { min-width: 0; }
.header-kicker { margin-bottom: 5px; color: var(--lime); font-size: 10px; font-weight: 700; letter-spacing: 1.3px; }
.profile-header h1 {
    margin: 0 0 4px; color: #fffdf6; font-family: Georgia, 'Times New Roman', serif;
    font-size: clamp(25px, 3vw, 34px); font-weight: 500; line-height: 1.1; letter-spacing: 0;
}
.profile-header h1 em { color: var(--coral); font-style: normal; }
.profile-header p { margin: 0; color: #d4e3db; font-size: 13px; line-height: 1.45; }
.website-link {
    display: inline-block; margin-top: 6px; color: var(--lime); font-size: 11px;
    font-weight: 700; text-decoration-thickness: 1px; text-underline-offset: 3px;
    overflow-wrap: anywhere;
}
.website-link:focus-visible { outline: 2px solid var(--coral); outline-offset: 3px; }
.header-stamp {
    display: grid; width: 62px; height: 62px; place-items: center; border: 1px solid #75998a;
    border-radius: 50%; color: var(--lime); font-family: Georgia, serif; font-size: 23px;
    transform: rotate(-8deg);
}
.prompt-label { margin: 0 0 6px 2px; color: var(--muted); font-size: 10px; font-weight: 700; letter-spacing: 1.2px; }
#prompt-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
#prompt-grid > * { width: 100%; min-width: 0; }
#prompt-grid button {
    min-height: 42px; padding: 7px 11px; border: 1px solid var(--line) !important;
    border-radius: 7px !important; background: rgba(255, 255, 255, .72) !important;
    color: var(--ink) !important; font-size: 12px; line-height: 1.25; text-align: left;
    transition: border-color .16s ease, background .16s ease, transform .16s ease;
}
#prompt-grid button:hover { border-color: #8cae9d !important; background: #fff !important; transform: translateY(-1px); }
#profile-chat {
    flex: 1 1 auto; min-height: 0; padding: 0 !important; gap: 0 !important;
    border: 1px solid var(--line); border-radius: 11px; background: #fff;
    box-shadow: 0 8px 24px rgba(34, 71, 56, .06); overflow: hidden;
}
#chat-heading { min-height: 45px; padding: 0 17px; align-items: center; border-bottom: 1px solid #edf1ed; }
.chat-heading-title { color: var(--ink); font-size: 12px; font-weight: 700; }
.chat-heading-note { margin-top: 2px; color: var(--muted); font-size: 10px; }
.status-line { min-height: 0; margin: 0 !important; color: var(--green); font-size: 10px; font-weight: 700; }
#profile-chatbot { flex: 1 1 auto; min-height: 0 !important; height: 0 !important; }
#profile-chatbot > div, #profile-chatbot .wrap { height: 100% !important; min-height: 0 !important; }
#composer {
    flex-wrap: nowrap !important; padding: 9px 12px 7px;
    align-items: center; border-top: 1px solid #edf1ed; gap: 8px;
}
#composer > .form { flex: 1 1 auto !important; width: auto !important; min-width: 0 !important; margin: 0 !important; }
#composer > #send-button, #composer > #clear-button { flex: 0 0 76px !important; width: 76px !important; min-width: 76px !important; margin: 0 !important; }
#query-box textarea { min-height: 42px !important; max-height: 84px; border-color: var(--line) !important; border-radius: 7px !important; background: #f8faf8 !important; }
#send-button { min-width: 82px; height: 42px; border: 0 !important; border-radius: 7px !important; background: var(--green) !important; color: white !important; }
#clear-button { min-width: 76px; height: 42px; border: 1px solid var(--line) !important; border-radius: 7px !important; background: white !important; color: var(--ink) !important; }
.privacy-note { margin: 0 !important; padding: 0 14px 9px; color: #72817b; font-size: 10px; line-height: 1.35; }
footer { display: none !important; }
@media (max-width: 700px) {
    .gradio-container { padding: 9px !important; }
    #app-shell { gap: 7px; }
    .profile-header { padding: 14px 16px; column-gap: 10px; border-radius: 10px; }
    .profile-header { grid-template-columns: 1fr; }
    .profile-header h1 { font-size: 23px; }
    .profile-header p { max-width: 440px; font-size: 11px; }
    .website-link { margin-top: 4px; font-size: 10px; }
    .header-stamp { display: none; }
    .header-kicker { font-size: 9px; }
    .prompt-label { margin-bottom: 4px; }
    #prompt-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px; }
    #prompt-grid button { min-height: 34px; padding: 5px 7px; font-size: 10px; }
    #chat-heading { min-height: 37px; padding: 0 11px; }
    .chat-heading-title { white-space: nowrap; font-size: 10px; }
    .chat-heading-note { display: none; }
    #composer { padding: 7px 8px 5px; gap: 5px; }
    #query-box textarea { min-height: 44px !important; font-size: 12px; line-height: 1.2; }
    #composer > #send-button, #composer > #clear-button { flex-basis: 56px !important; width: 56px !important; min-width: 56px !important; height: 38px; padding: 0 4px !important; font-size: 10px; }
    .privacy-note { padding: 0 9px 7px; font-size: 9px; }
}
@media (max-height: 680px) and (min-width: 701px) {
    .gradio-container { padding-top: 8px !important; padding-bottom: 8px !important; }
    #app-shell { gap: 6px; }
    .profile-header { padding: 12px 20px; }
    .header-stamp { width: 46px; height: 46px; }
    #prompt-grid button { min-height: 36px; }
}
"""


def respond(
    message: str, session_history: list[dict[str, str]] | None
) -> tuple[list[dict[str, str]], list[dict[str, str]], str, str]:
    question = message.strip()
    history = list(session_history or [])
    if not question:
        return history, history, "", "Type a question to get started."

    recent = history[-12:]
    answer = run_profile_graph(question, recent)
    updated = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    return updated, updated, "", "Ready"


def clear_conversation() -> tuple[list[dict[str, str]], list[dict[str, str]], str, str]:
    return [], [], "", "Conversation cleared."


with (
    gr.Blocks(
        title="Ask Questions About Subhadeep",
        theme=gr.themes.Soft(primary_hue="emerald", neutral_hue="slate"),
        css=CSS,
    ) as demo,
    gr.Column(elem_id="app-shell"),
):
    gr.HTML(
        """<header class="profile-header">
          <div class="header-copy">
            <div class="header-kicker">PROFILE CONVERSATION</div>
            <h1>Ask Questions About <em>Subhadeep</em></h1>
            <p>Career, skills, projects, education, and professional interests.</p>
                        <a class="website-link" href="https://www.subhadeepsengupta.com/" target="_blank" rel="noopener noreferrer">www.subhadeepsengupta.com</a>
          </div>
          <div class="header-stamp" aria-hidden="true">SS</div>
        </header>"""
    )

    conversation = gr.State([])
    gr.Markdown("START WITH A QUESTION", elem_classes="prompt-label")
    prompts = [
        "What are Subhadeep's key technical skills?",
        "Tell me about Subhadeep's recent projects.",
        "What type of roles is Subhadeep interested in?",
        "How can I get in touch about an opportunity?",
    ]
    with gr.Row(elem_id="prompt-grid"):
        prompt_buttons = [gr.Button(prompt) for prompt in prompts]

    with gr.Column(elem_id="profile-chat"):
        with gr.Row(elem_id="chat-heading"):
            with gr.Column(scale=1, min_width=0):
                gr.HTML(
                    '<div class="chat-heading-title">YOUR CONVERSATION</div>'
                    '<div class="chat-heading-note">Grounded in Subhadeep\'s profile</div>'
                )
            status = gr.Markdown("READY", elem_classes="status-line")
        chatbot = gr.Chatbot(
            type="messages",
            height="100%",
            elem_id="profile-chatbot",
            show_label=False,
            allow_tags=False,
            placeholder="Ask about Subhadeep's experience, projects, or career interests.",
        )
    with gr.Row(elem_id="composer"):
        message = gr.Textbox(
            placeholder="Ask a question about Subhadeep...",
            show_label=False,
            lines=1,
            scale=8,
            autofocus=True,
            elem_id="query-box",
        )
        send = gr.Button("Send", variant="primary", scale=1, min_width=82, elem_id="send-button")
        clear = gr.Button("Clear", variant="secondary", scale=1, min_width=76, elem_id="clear-button")
    gr.Markdown(
        "Shared contact details may be saved so Subhadeep can follow up.",
        elem_classes="privacy-note",
    )

    outputs = [chatbot, conversation, message, status]
    for button, prompt in zip(prompt_buttons, prompts):
        button.click(lambda value=prompt: value, outputs=message)
    send.click(respond, inputs=[message, conversation], outputs=outputs)
    message.submit(respond, inputs=[message, conversation], outputs=outputs)
    clear.click(clear_conversation, outputs=outputs)


if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(__import__("os").getenv("PORT", "7860")),
        show_error=False,
    )