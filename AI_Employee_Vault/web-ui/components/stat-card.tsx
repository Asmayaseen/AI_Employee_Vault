interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  color?: "blue" | "green" | "amber" | "red" | "purple";
}

const colorMap = {
  blue: "bg-[#0097A715] text-[#0097A7] dark:bg-[#00E5FF15] dark:text-[#00E5FF]",
  green: "bg-[#00C85315] text-[#00C853] dark:bg-[#39FF1415] dark:text-[#39FF14]",
  amber: "bg-[#FF6B0015] text-[#E65100] dark:bg-[#FF6B0015] dark:text-[#FF8C00]",
  red: "bg-[#FF2D5515] text-[#DC2626] dark:bg-[#FF2D5515] dark:text-[#FF2D55]",
  purple: "bg-[#A855F715] text-[#9333EA] dark:bg-[#A855F715] dark:text-[#C084FC]",
};

export default function StatCard({ label, value, icon, color = "blue" }: StatCardProps) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`rounded-lg p-3 ${colorMap[color]}`}>
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
        </svg>
      </div>
      <div>
        <p className="text-sm text-[#555555] dark:text-[#8899AA]">{label}</p>
        <p className="text-2xl font-bold text-[#0A0A0A] dark:text-[#F0F0F0]">{value}</p>
      </div>
    </div>
  );
}
