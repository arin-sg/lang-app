import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function CoachPage() {
  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-extrabold tracking-tight">Coach Chat</h1>
      <Card className="border-2">
        <CardContent className="pt-10 pb-10 text-center space-y-6">
          <div className="text-7xl">💬</div>
          <div className="space-y-3">
            <h2 className="text-3xl font-extrabold">Coming in Iteration 2</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              The Coach Chat feature will provide targeted conversation practice
              with AI feedback to help you use specific vocabulary and patterns.
            </p>
          </div>
          <Card className="border bg-muted/30 max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-xl">Planned Features:</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-left">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold">•</span>
                  <span>Targeted chat sessions based on your review items</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold">•</span>
                  <span>Real-time feedback on your responses</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold">•</span>
                  <span>"Patch notes" summary of corrections</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold">•</span>
                  <span>Error classification and tracking</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  );
}
