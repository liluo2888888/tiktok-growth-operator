import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { ui } from "@/lib/copy";

export function LegalPage() {
  return (
    <>
      <PageHero
        kicker="法律"
        title="隐私与语音数据"
        lead={`Quest English / ${ui.brand.title} MVP 测试版说明`}
      />

      <div className="stack">
        <Panel title="我们存储什么">
          <p className="card-body">
            练习回答、得分与护照印章会保存在你的浏览器及我们的后端，用于练习记录。我们不会出售你的数据。
          </p>
        </Panel>
        <Panel title="移动端语音">
          <p className="card-body">
            移动端 App 在录音作答时可能将音频发送至第三方语音识别服务。本 Web 端仅支持打字作答。
          </p>
        </Panel>
        <Panel title="测试版说明">
          <p className="card-body">
            测试期间数据可能被重置。请勿在练习回答中使用雇主机密或敏感信息。
          </p>
        </Panel>
      </div>
    </>
  );
}
