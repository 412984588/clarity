import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-3xl px-6 py-16">
        <Button asChild variant="ghost" className="mb-8">
          <Link href="/">
            <ArrowLeft className="mr-2 size-4" />
            返回首页
          </Link>
        </Button>

        <h1 className="mb-8 text-4xl font-bold">隐私政策</h1>
        <p className="mb-8 text-muted-foreground">最后更新：2025 年 12 月</p>

        <div className="prose prose-neutral max-w-none dark:prose-invert">
          <h2>1. 信息收集</h2>
          <p>Solacore 收集的信息仅限于为您提供服务所必需的内容，包括：</p>
          <ul>
            <li>账户信息：您注册时提供的邮箱地址</li>
            <li>对话内容：您与 AI 助手的对话记录</li>
            <li>使用数据：基本的使用统计信息</li>
          </ul>

          <h2>2. 信息使用</h2>
          <p>我们使用收集的信息用于：</p>
          <ul>
            <li>提供、维护和改进我们的服务</li>
            <li>个性化您的使用体验</li>
            <li>与您沟通服务相关事项</li>
          </ul>

          <h2>3. 信息保护</h2>
          <p>
            我们采取行业标准的安全措施保护您的个人信息，包括数据加密、
            访问控制和安全审计。您的对话内容经过加密存储，仅您本人可以访问。
          </p>

          <h2>4. 信息共享</h2>
          <p>
            我们不会出售、交易或以其他方式向外部方转让您的个人身份信息。
            这不包括协助我们运营网站、开展业务或为您提供服务的可信第三方，
            前提是这些方同意对这些信息保密。
          </p>

          <h2>5. Cookie 使用</h2>
          <p>
            我们使用 Cookie 来维护您的登录状态和偏好设置。您可以选择在
            浏览器设置中禁用 Cookie，但这可能会影响某些功能的使用。
          </p>

          <h2>6. 您的权利</h2>
          <p>您有权：</p>
          <ul>
            <li>访问和导出您的个人数据</li>
            <li>更正不准确的信息</li>
            <li>删除您的账户和相关数据</li>
            <li>撤回对数据处理的同意</li>
          </ul>

          <h2>7. 联系我们</h2>
          <p>
            如果您对本隐私政策有任何疑问，请通过 support@solacore.app
            与我们联系。
          </p>
        </div>
      </div>
    </div>
  );
}
