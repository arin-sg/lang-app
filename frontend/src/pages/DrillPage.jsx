import { useState, useEffect } from 'react';
import { getDrillSession, gradeDrill } from '../api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle } from 'lucide-react';

import ClozeDrill from '../components/drills/ClozeDrill';
import PatternDrill from '../components/drills/PatternDrill';
import SaboteurDrill from '../components/drills/SaboteurDrill';

export default function DrillPage() {
  const [queue, setQueue] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [grading, setGrading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDrills();
  }, []);

  const loadDrills = async () => {
    try {
      setLoading(true);
      const drills = await getDrillSession(10);
      setQueue(drills);
      setCurrentIndex(0);
      setError(null);
    } catch (err) {
      setError('Failed to load drills. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (answer) => {
    const currentDrill = queue[currentIndex];

    setGrading(true);
    setFeedback(null);

    try {
      const result = await gradeDrill({
        drill_type: currentDrill.type,
        user_answer: answer,
        target_lemma: currentDrill.target_lemma,
        context: currentDrill.meta.original_sentence,
        question_meta: currentDrill.meta
      });

      setFeedback(result);

      // Wait 2 seconds, then move to next drill
      setTimeout(() => {
        if (currentIndex < queue.length - 1) {
          setCurrentIndex(currentIndex + 1);
          setFeedback(null);
        } else {
          // Session complete
          setFeedback({ ...result, sessionComplete: true });
        }
      }, 2000);
    } catch (err) {
      setError('Failed to grade answer. Please try again.');
    } finally {
      setGrading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-muted-foreground">Loading drills...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (queue.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <p className="text-lg text-muted-foreground">
            No drills available. Try extracting some German text first!
          </p>
        </CardContent>
      </Card>
    );
  }

  const currentDrill = queue[currentIndex];
  const progress = `${currentIndex + 1}/${queue.length}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-extrabold">Active Drills</h1>
        <Badge variant="outline" className="text-lg px-4 py-2">
          {progress}
        </Badge>
      </div>

      {/* Drill Component */}
      {currentDrill.type === 'cloze' && (
        <ClozeDrill drill={currentDrill} onSubmit={handleSubmit} />
      )}
      {currentDrill.type === 'pattern' && (
        <PatternDrill drill={currentDrill} onSubmit={handleSubmit} />
      )}
      {currentDrill.type === 'saboteur' && (
        <SaboteurDrill drill={currentDrill} onSubmit={handleSubmit} />
      )}

      {/* Feedback */}
      {feedback && !feedback.sessionComplete && (
        <Alert variant={feedback.is_correct ? 'default' : 'destructive'}>
          <div className="flex items-center gap-3">
            {feedback.is_correct ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <XCircle className="w-6 h-6 text-destructive" />
            )}
            <AlertDescription className="text-lg">
              {feedback.feedback}
            </AlertDescription>
          </div>
        </Alert>
      )}

      {/* Session Complete */}
      {feedback?.sessionComplete && (
        <Card className="border-2 bg-gradient-to-br from-primary/10 to-primary/5">
          <CardContent className="pt-6 text-center space-y-4">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto" />
            <h2 className="text-2xl font-extrabold">Session Complete!</h2>
            <p className="text-muted-foreground">
              You've completed all drills for today.
            </p>
            <Button onClick={loadDrills} size="lg" className="mt-4">
              Start New Session
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
