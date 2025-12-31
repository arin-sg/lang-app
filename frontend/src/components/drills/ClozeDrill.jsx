import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function ClozeDrill({ drill, onSubmit }) {
  const [answer, setAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (!answer.trim()) return;
    setSubmitted(true);
    onSubmit(answer);
  };

  // Split question by blank marker
  const parts = drill.question.split('________');

  return (
    <Card className="border-2">
      <CardContent className="pt-6 space-y-4">
        <div className="text-lg">
          {parts[0]}
          <Input
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            disabled={submitted}
            className="inline-block w-48 mx-2"
            placeholder="..."
          />
          {parts[1]}
        </div>

        {drill.meta.hint && (
          <Alert>
            <AlertDescription>
              💡 Hint: {drill.meta.hint}
            </AlertDescription>
          </Alert>
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
