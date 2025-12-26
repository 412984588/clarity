import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/api/",
          "/dashboard/",
          "/solve/",
          "/sessions/",
          "/settings/",
          "/paywall/",
        ],
      },
    ],
    sitemap: "https://solacore.app/sitemap.xml",
  };
}
