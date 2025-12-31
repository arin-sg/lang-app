import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileCode } from 'lucide-react';

export default function PatternDrill({ drill, onSubmit }) {
  const [answer, setAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (!answer.trim()) return;
    setSubmitted(true);
    onSubmit(answer);
  };

  return (
    <Card className="border-2">
      <CardHeader>
        <div className="flex items-center gap-3">
          <FileCode className="w-6 h-6 text-primary flex-shrink-0" />
          <CardTitle className="font-mono">{drill.meta.template}</CardTitle>
          <Badge variant="secondary" className="flex-shrink-0">Pattern</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-muted-foreground italic">
          {drill.meta.english_gloss}
        </p>

        <div>
          <label className="font-semibold mb-2 block">
            {drill.question}
          </label>
          <Textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={submitted}
            placeholder="Type your sentence here..."
            className="min-h-[100px]"
          />
        </div>

        {drill.meta.hint && (
          <p className="text-sm text-muted-foreground">
            💡 {drill.meta.hint}
          </p>
        )}

        <Button
          onClick={handleSubmit}
          disabled={!answer.trim() || submitted}
          className="w-full"
        >
          Submit Answer
        </Button>
      </CardContent>
    </Card>
  );
}
