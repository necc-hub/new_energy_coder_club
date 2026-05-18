import {
  Wrench,
  RotateCw,
  Cpu,
  Camera,
  TerminalSquare,
  Sparkles,
} from "lucide-react";
import { useTranslation } from "@/contexts/LanguageContext";

// Add a type assertion for the icon names
const iconMap: { [key: string]: React.FC<React.SVGProps<SVGSVGElement>> } = {
  Wrench,
  RotateCw,
  Cpu,
  Camera,
  TerminalSquare,
  Sparkles,
};

export function AboutSection() {
  const t = useTranslation();

  // Ensure core_competencies is an array before mapping
  const competencies = t.about.core_competencies || [];

  return (
    <section className="py-24 bg-background">
      <div className="container">
        <h1 className="text-4xl font-bold tracking-tight text-center sm:text-5xl md:text-6xl mb-6 gradient-text">
          {t.footer.clubName}
        </h1>
        <p className="leading-relaxed text-center max-w-4xl mx-auto text-lg mb-12 text-muted-foreground">
          {t.about.paragraph1}
        </p>

        <div className="space-y-4 max-w-3xl mx-auto">
          {competencies.map((competency, index) => {
            // Default to a placeholder icon if the specified icon doesn't exist
            const Icon = competency.icon ? iconMap[competency.icon] : Sparkles;
            return (
              <div
                key={index}
                className="flex items-center gap-4 p-4 rounded-lg bg-secondary/50 border border-border/50 hover:bg-secondary/80 transition-colors"
              >
                <div className="p-2 rounded-lg bg-primary/10">
                  {Icon && <Icon className="h-6 w-6 text-primary" />}
                </div>
                <p className="text-foreground">
                  <span className="font-bold text-base text-primary">
                    {competency.category}:
                  </span>{" "}
                  {competency.skills}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
