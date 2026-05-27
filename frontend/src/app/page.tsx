import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <h1 className="mb-4 text-4xl font-bold text-slate-900 dark:text-white">
        AI 私人家教
      </h1>
      <p className="mb-8 max-w-md text-lg text-slate-600 dark:text-slate-400">
        AI-powered private tutor for AMC math &amp; KET English
      </p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          登录
        </Link>
        <Link
          href="/register"
          className="rounded-lg border border-slate-300 px-6 py-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          注册
        </Link>
      </div>
    </div>
  );
}
