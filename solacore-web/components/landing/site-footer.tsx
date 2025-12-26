import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t bg-background py-12">
      <div className="container mx-auto flex flex-col items-center justify-between gap-6 px-6 md:flex-row">
        <div className="flex items-center gap-2">
          <div className="size-6 rounded bg-gradient-to-br from-amber-200 to-emerald-200" />
          <p className="text-sm font-semibold">Solacore &copy; 2025</p>
        </div>
        <div className="flex gap-8 text-sm text-muted-foreground">
          <Link href="/privacy" className="hover:text-foreground">
            隐私政策
          </Link>
          <Link href="/terms" className="hover:text-foreground">
            服务条款
          </Link>
          <Link
            href="mailto:support@solacore.com"
            className="hover:text-foreground"
          >
            联系我们
          </Link>
        </div>
      </div>
    </footer>
  );
}
