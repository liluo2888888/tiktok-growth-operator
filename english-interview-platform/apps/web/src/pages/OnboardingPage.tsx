import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { PageHero } from "@/components/ui/PageHero";
import { Selectable } from "@/components/ui/Selectable";
import { StepIndicator } from "@/components/ui/StepIndicator";
import { track } from "@/lib/analytics";
import { GOALS, ROLES } from "@/lib/quests";
import { getProfile, saveProfile } from "@/lib/storage";

export function OnboardingPage() {
  const navigate = useNavigate();
  const existing = getProfile();
  const [step, setStep] = useState<1 | 2>(1);
  const [roleId, setRoleId] = useState<"product" | "general">("product");

  if (existing?.completedOnboarding) {
    return <Navigate to="/" replace />;
  }

  function finish() {
    const role = ROLES.find((r) => r.id === roleId)!;
    saveProfile({ goal: "job_interview", roleId, roleLabel: role.label });
    void track("onboarding_complete", { goal: "job_interview", roleId });
    navigate("/quest-map");
  }

  return (
    <>
      <PageHero
        kicker="欢迎"
        title="设置你的面试 Quest"
        lead="我们会根据你的目标与岗位定制任务。"
      />

      <StepIndicator current={step} total={2} labels={["目标", "岗位"]} />

      {step === 1 && (
        <div className="stack" style={{ maxWidth: "36rem" }}>
          <h2 className="panel-title">你在准备什么？</h2>
          {GOALS.map((goal) => (
            <Selectable
              key={goal.id}
              title={goal.label}
              description={goal.description}
              selected
              badge="MVP"
            />
          ))}
          <Button onClick={() => setStep(2)}>下一步</Button>
        </div>
      )}

      {step === 2 && (
        <div className="stack" style={{ maxWidth: "36rem" }}>
          <h2 className="panel-title">选择岗位赛道</h2>
          {ROLES.map((role) => (
            <Selectable
              key={role.id}
              title={role.label}
              description={role.description}
              selected={roleId === role.id}
              onClick={() => setRoleId(role.id)}
            />
          ))}
          <Link to="/legal" className="btn-ghost btn" style={{ width: "fit-content" }}>
            隐私与语音数据说明
          </Link>
          <div className="row">
            <Button variant="secondary" onClick={() => setStep(1)}>
              上一步
            </Button>
            <Button onClick={finish}>进入任务地图</Button>
          </div>
        </div>
      )}
    </>
  );
}
