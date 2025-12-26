import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-3xl px-6 py-16">
        <Button asChild variant="ghost" className="mb-8">
          <Link href="/">
            <ArrowLeft className="mr-2 size-4" />
            返回首页
          </Link>
        </Button>

        <h1 className="mb-8 text-4xl font-bold">服务条款</h1>
        <p className="mb-8 text-muted-foreground">最后更新：2025 年 12 月</p>

        <div className="prose prose-neutral max-w-none dark:prose-invert">
          <h2>1. 服务说明</h2>
          <p>
            Solacore 是一个 AI 驱动的情绪梳理助手，旨在帮助用户通过结构化的
            对话流程，将复杂情绪转化为清晰的行动计划。本服务不构成专业的
            心理咨询或医疗建议。
          </p>

          <h2>2. 使用条件</h2>
          <p>使用 Solacore 服务，您需要：</p>
          <ul>
            <li>年满 18 周岁或在监护人监督下使用</li>
            <li>提供准确的注册信息</li>
            <li>妥善保管您的账户凭证</li>
            <li>遵守所有适用的法律法规</li>
          </ul>

          <h2>3. 禁止行为</h2>
          <p>您不得：</p>
          <ul>
            <li>滥用或试图破坏服务</li>
            <li>上传恶意内容或进行非法活动</li>
            <li>未经授权访问他人账户</li>
            <li>干扰服务的正常运行</li>
          </ul>

          <h2>4. 知识产权</h2>
          <p>
            Solacore 的所有内容、功能和界面设计均受知识产权法保护。
            您在使用过程中创建的对话内容归您所有，但您授予我们处理
            这些内容以提供服务的许可。
          </p>

          <h2>5. 免责声明</h2>
          <p>
            Solacore 按「现状」提供服务。我们不保证服务不会中断或无错误。 AI
            生成的建议仅供参考，不构成专业意见。如果您正在经历严重的
            心理困扰，请寻求专业心理健康服务。
          </p>

          <h2>6. 责任限制</h2>
          <p>
            在法律允许的最大范围内，Solacore 不对因使用或无法使用服务
            而导致的任何间接、附带、特殊或后果性损害负责。
          </p>

          <h2>7. 服务变更</h2>
          <p>
            我们保留随时修改或终止服务（或其任何部分）的权利，无论是否通知。
            我们对您或任何第三方不承担因服务修改、暂停或终止而产生的责任。
          </p>

          <h2>8. 条款修改</h2>
          <p>
            我们可能会不时更新这些条款。更新后的条款将在网站上发布，
            继续使用服务即表示您接受修改后的条款。
          </p>

          <h2>9. 联系方式</h2>
          <p>
            如果您对本服务条款有任何疑问，请通过 support@solacore.app
            与我们联系。
          </p>
        </div>
      </div>
    </div>
  );
}
