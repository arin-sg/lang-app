import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';

export default function SaboteurDrill({ drill, onSubmit }) {
  const [answer, setAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (!answer.trim()) return;
    setSubmitted(true);
    onSubmit(answer);
  };

  return (
    <Card className="border-2 border-destructive/50">
      <CardHeader className="bg-destructive/10">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-destructive" />
          <CardTitle>Fix the Error!</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="pt-6 space-y-4">
        <Alert variant="destructive">
          <AlertDescription className="text-lg font-semibold">
            {drill.question}
          </AlertDescription>
        </Alert>

        {drill.meta.hint && (
          <p className="text-sm text-muted-foreground">
            💡 {drill.meta.hint}
          </p>
        )}

        <div>
          <label className="font-semibold mb-2 block">
            Corrected sentence:
          </label>
          <Textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={submitted}
            placeholder="Type the corrected sentence..."
            className="min-h-[100px]"
          />
        </div>

        <Button
          onClick={handleSubmit}
          disabled={!answer.trim() || submitted}
          className="w-full"
        >
          Submit Correction
        </Button>
      </CardContent>
    </Card>
  );
}
