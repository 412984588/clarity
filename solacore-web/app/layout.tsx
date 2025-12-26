import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AuthProvider } from "@/components/auth/AuthProvider";
import { ThemeProvider } from "@/components/shared/ThemeProvider";
import { Toaster } from "@/components/ui/sonner";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://solacore.app"),
  title: {
    default: "Solacore - AI 情绪梳理助手 | 把焦虑转化为行动",
    template: "%s | Solacore",
  },
  description:
    "Solacore 是基于 CBT 认知行为疗法的 AI 情绪梳理助手。通过 5 步引导流程，帮你把复杂的情绪转化为清晰的行动计划，从混乱中找回掌控感。",
  keywords: [
    "情绪管理",
    "焦虑缓解",
    "AI 助手",
    "认知行为疗法",
    "CBT",
    "心理健康",
    "情绪梳理",
    "行动计划",
    "自我成长",
    "Solacore",
  ],
  authors: [{ name: "Solacore Team" }],
  creator: "Solacore",
  openGraph: {
    type: "website",
    locale: "zh_CN",
    url: "https://solacore.app",
    title: "Solacore - AI 情绪梳理助手",
    description:
      "把复杂的情绪转化为清晰的行动。基于 CBT 认知行为疗法的 5 步引导流程。",
    siteName: "Solacore",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Solacore - AI 情绪梳理助手",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Solacore - AI 情绪梳理助手",
    description:
      "把复杂的情绪转化为清晰的行动。基于 CBT 认知行为疗法的 5 步引导流程。",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "https://solacore.app",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
