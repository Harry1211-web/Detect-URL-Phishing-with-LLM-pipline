const SAMPLES = [
  { label: "Real Vietcombank site", url: "https://www.vietcombank.com.vn/" },
  { label: "Sample fake site", url: "http://vietcombamk-xacthuc.com/login" },
  { label: "Hidden domain trick", url: "https://vietcombank.com.vn@example.com/login" },
];

interface Props {
  disabled: boolean;
  onPick: (url: string) => void;
}

// Samples only fill the input: nothing here navigates to a URL
export default function SampleUrls({ disabled, onPick }: Props) {
  return (
    <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
      <span className="text-muted">Try it with:</span>
      {SAMPLES.map((sample) => (
        <button
          key={sample.url}
          type="button"
          disabled={disabled}
          onClick={() => onPick(sample.url)}
          className="font-semibold text-brand underline underline-offset-4 disabled:opacity-60"
        >
          {sample.label}
        </button>
      ))}
    </div>
  );
}
