import { useState, useEffect } from 'react';
import { getReviewDeck, submitReviewResult } from '../api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function ReviewPage() {
  const [deck, setDeck] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [startTime, setStartTime] = useState(null);

  // Flip-card mode state
  const [reviewMode, setReviewMode] = useState('flip'); // 'flip' or 'input'
  const [isFlipped, setIsFlipped] = useState(false);
  const [selfGraded, setSelfGraded] = useState(null); // 'correct' | 'incorrect' | null

  useEffect(() => {
    loadDeck();
  }, []);

  const loadDeck = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getReviewDeck();
      setDeck(data.deck);
      setStartTime(Date.now());
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load review deck');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const currentItem = deck[currentIndex];
    const correct = userAnswer.trim().toLowerCase() === currentItem.canonical_form.toLowerCase();
    const responseTime = Date.now() - startTime;

    setIsCorrect(correct);
    setShowFeedback(true);

    // Record result
    try {
      await submitReviewResult({
        item_id: currentItem.item_id,
        correct,
        actual_answer: userAnswer,
        expected_answer: currentItem.canonical_form,
        prompt: `What is the German for: ${currentItem.metadata.english_gloss || 'this item'}`,
        response_time_ms: responseTime
      });
    } catch (err) {
      console.error('Failed to record result:', err);
    }
  };

  const handleNext = () => {
    if (currentIndex < deck.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setUserAnswer('');
      setShowFeedback(false);
      setIsFlipped(false);
      setSelfGraded(null);
      setStartTime(Date.now());
    }
  };

  const handleSelfGrade = async (correct) => {
    setSelfGraded(correct);
    const responseTime = Date.now() - startTime;
    const currentItem = deck[currentIndex];

    // Record result (same API as input mode)
    try {
      await submitReviewResult({
        item_id: currentItem.item_id,
        correct,
        actual_answer: correct ? currentItem.canonical_form : "",
        expected_answer: currentItem.canonical_form,
        prompt: `What is the German for: ${currentItem.metadata.english_gloss || 'this item'}`,
        response_time_ms: responseTime
      });
    } catch (err) {
      console.error('Failed to record result:', err);
    }

    // Auto-advance after brief delay
    setTimeout(() => {
      handleNext();
    }, 800);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg font-semibold text-muted-foreground">Loading review deck...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <Alert variant="destructive" className="border-2">
          <AlertDescription className="font-semibold">
            {error}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (deck.length === 0) {
    return (
      <div className="space-y-8">
        <h1 className="text-4xl font-extrabold tracking-tight">Review Deck</h1>
        <Card className="border-2">
          <CardContent className="pt-10 pb-10 text-center">
            <p className="text-lg font-semibold text-muted-foreground mb-2">No items to review yet!</p>
            <p className="text-muted-foreground">Go to the Ingest page to add some German text first.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentItem = deck[currentIndex];
  const progressPercent = ((currentIndex + 1) / deck.length) * 100;

  if (currentIndex >= deck.length) {
    return (
      <div className="space-y-8">
        <h1 className="text-4xl font-extrabold tracking-tight">Review Complete!</h1>
        <Card className="border-2">
          <CardContent className="pt-10 pb-10 text-center space-y-4">
            <p className="text-2xl font-bold">You've finished reviewing all {deck.length} items.</p>
            <Button onClick={loadDeck} size="lg" className="font-extrabold">
              Load New Deck
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Progress */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-4xl font-extrabold tracking-tight">Review Deck</h1>
          <Badge variant="secondary" className="text-lg font-extrabold px-4 py-2">
            {currentIndex + 1} / {deck.length}
          </Badge>
        </div>
        <Progress value={progressPercent} className="h-3" />
      </div>

      {/* Mode Selector */}
      <div className="flex gap-2">
        <Button
          variant={reviewMode === 'flip' ? 'default' : 'secondary'}
          onClick={() => setReviewMode('flip')}
          className="font-semibold flex-1"
        >
          Flip Card
        </Button>
        <Button
          variant={reviewMode === 'input' ? 'default' : 'secondary'}
          onClick={() => setReviewMode('input')}
          className="font-semibold flex-1"
        >
          Type Answer
        </Button>
      </div>

      {/* Review Content */}
      {reviewMode === 'flip' ? (
        <FlipCardReview
          item={currentItem}
          onGrade={handleSelfGrade}
          isFlipped={isFlipped}
          onFlip={() => setIsFlipped(true)}
          selfGraded={selfGraded}
        />
      ) : (
        <Card className="border-2">
          <CardContent className="pt-8 pb-8">
            <div className="space-y-6">
              {/* Type Badge */}
              <div className="flex justify-center">
                <Badge variant="secondary" className="text-sm font-semibold">
                  {currentItem.type}
                </Badge>
              </div>

              {/* Question */}
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-extrabold">What is this in German?</h2>
                <p className="text-3xl text-primary font-bold">
                  {currentItem.metadata.english_gloss || currentItem.canonical_form}
                </p>
              </div>

              {/* Answer Form or Feedback */}
              {!showFeedback ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <Input
                    type="text"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Type your answer..."
                    className="text-xl h-14 text-center border-2"
                    autoFocus
                  />
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full font-extrabold text-lg"
                    disabled={!userAnswer.trim()}
                  >
                    Check Answer
                  </Button>
                </form>
              ) : (
                <div className={`p-6 rounded-lg border-2 space-y-4 text-center ${
                  isCorrect ? 'bg-green-50 border-green-500' : 'bg-red-50 border-destructive'
                }`}>
                  <div className="text-6xl">{isCorrect ? '✓' : '✗'}</div>
                  <p className="text-2xl font-extrabold">
                    {isCorrect ? 'Correct!' : 'Incorrect'}
                  </p>
                  {!isCorrect && (
                    <div className="bg-card p-4 rounded-lg">
                      <strong className="text-muted-foreground">Correct answer:</strong>
                      <p className="text-2xl font-bold mt-2">{currentItem.canonical_form}</p>
                    </div>
                  )}
                  <Button onClick={handleNext} size="lg" className="font-extrabold">
                    {currentIndex < deck.length - 1 ? 'Next →' : 'Finish'}
                  </Button>
                </div>
              )}

              {/* Metadata */}
              {currentItem.metadata && (
                <div className="flex justify-center gap-2 flex-wrap">
                  {currentItem.metadata.cefr_guess && (
                    <Badge variant="outline" className="font-semibold">
                      CEFR: {currentItem.metadata.cefr_guess}
                    </Badge>
                  )}
                  {currentItem.metadata.gender && (
                    <Badge variant="outline" className="font-semibold">
                      Gender: {currentItem.metadata.gender}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Flip Card Review Component
function FlipCardReview({ item, onGrade, isFlipped, onFlip, selfGraded }) {
  const englishGloss = item.metadata?.english_gloss || 'No translation available';

  return (
    <div className="min-h-[400px] flex items-center justify-center">
      {!isFlipped ? (
        // FRONT: Show question
        <Card className="border-2 w-full max-w-2xl">
          <CardContent className="pt-10 pb-10 text-center space-y-6">
            <Badge variant="secondary" className="text-sm font-semibold">
              {item.type === 'chunk' ? 'Phrase' : item.type.charAt(0).toUpperCase() + item.type.slice(1)}
            </Badge>
            <div className="space-y-4">
              <p className="text-xl font-semibold text-muted-foreground">What is this in German?</p>
              <h2 className="text-4xl font-extrabold text-primary">{englishGloss}</h2>
            </div>
            {item.metadata && (
              <div className="flex justify-center gap-2 flex-wrap">
                {item.metadata.cefr_guess && (
                  <Badge variant="outline" className="font-semibold">
                    CEFR: {item.metadata.cefr_guess}
                  </Badge>
                )}
                {item.metadata.gender && (
                  <Badge variant="outline" className="font-semibold">
                    Gender: {item.metadata.gender}
                  </Badge>
                )}
              </div>
            )}
            <Button onClick={onFlip} size="lg" className="font-extrabold text-lg mt-6">
              Show Answer
            </Button>
          </CardContent>
        </Card>
      ) : (
        // BACK: Show answer and self-grading
        <Card className="border-2 w-full max-w-2xl bg-gradient-to-br from-primary/5 to-accent/10">
          <CardContent className="pt-10 pb-10 text-center space-y-6">
            <div className="space-y-2">
              <h2 className="text-5xl font-extrabold">{item.canonical_form}</h2>
              <p className="text-xl text-muted-foreground italic">{englishGloss}</p>
            </div>
            {!selfGraded ? (
              <div className="space-y-4">
                <p className="text-lg font-semibold text-muted-foreground">Did you get it right?</p>
                <div className="flex gap-4 justify-center">
                  <Button
                    variant="destructive"
                    size="lg"
                    onClick={() => onGrade(false)}
                    className="font-extrabold text-lg flex-1 max-w-xs"
                  >
                    ✗ I didn't know
                  </Button>
                  <Button
                    size="lg"
                    onClick={() => onGrade(true)}
                    className="font-extrabold text-lg flex-1 max-w-xs bg-green-600 hover:bg-green-700"
                  >
                    ✓ I knew it
                  </Button>
                </div>
              </div>
            ) : (
              <div className={`p-6 rounded-lg ${selfGraded ? 'bg-green-100' : 'bg-red-100'}`}>
                <div className="text-6xl mb-2">{selfGraded ? '✓' : '✗'}</div>
                <p className="text-xl font-bold">{selfGraded ? 'Great job!' : 'Keep practicing!'}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
