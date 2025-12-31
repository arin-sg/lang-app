import { useState } from 'react';
import { ingestText } from '../api/client';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

export default function IngestPage() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Character limit
  const CHAR_LIMIT = 500;
  const charCount = text.length;
  const isOverLimit = charCount > CHAR_LIMIT;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!text.trim()) {
      setError('Please enter some German text');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await ingestText(text);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process text. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight">Ingest German Text</h1>
        <p className="text-muted-foreground text-lg">Paste German text below to extract learnable items</p>
      </div>

      {/* Input Form */}
      <Card className="border-2">
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Character Counter */}
            <div className="flex justify-between items-center mb-2">
              <label className="font-semibold text-sm text-muted-foreground">German Text Input</label>
              <span className={`text-sm font-semibold ${
                isOverLimit ? 'text-destructive' : 'text-muted-foreground'
              }`}>
                {charCount}/{CHAR_LIMIT}
              </span>
            </div>

            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your German text here...&#10;&#10;Example:&#10;Ich muss heute eine wichtige Entscheidung treffen."
              className="min-h-[300px] bg-muted/30 border-2 text-base resize-none"
              disabled={loading}
            />

            {/* Over-limit warning */}
            {isOverLimit && (
              <Alert variant="destructive" className="border-2">
                <AlertDescription className="font-semibold">
                  Text is too long. Please shorten to {CHAR_LIMIT} characters or less.
                </AlertDescription>
              </Alert>
            )}

            <Button
              type="submit"
              size="lg"
              className="w-full font-extrabold text-lg h-14"
              disabled={loading || !text.trim() || isOverLimit}
            >
              {loading ? 'Processing...' : 'Extract Items'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="border-2">
          <AlertDescription className="font-semibold">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="border-2 bg-gradient-to-br from-primary/10 to-primary/5">
              <CardContent className="pt-6">
                <div className="text-center space-y-2">
                  <div className="text-5xl font-extrabold text-primary">{result.items_extracted}</div>
                  <div className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Items Extracted</div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-2 bg-gradient-to-br from-accent/30 to-accent/10">
              <CardContent className="pt-6">
                <div className="text-center space-y-2">
                  <div className="text-5xl font-extrabold text-accent-foreground">{result.edges_created}</div>
                  <div className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Relationships</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Extracted Items */}
          {result.items && result.items.length > 0 && (
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-2xl">Extracted Items</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.items.map((item) => (
                    <Card key={item.id} className="border bg-muted/20">
                      <CardContent className="pt-4 space-y-2">
                        <div className="flex items-center justify-between gap-4">
                          <span className="text-lg font-bold">{item.canonical_form}</span>
                          <Badge variant="secondary" className="font-semibold">
                            {item.type === 'chunk' ? 'Phrase' : item.type.charAt(0).toUpperCase() + item.type.slice(1)}
                          </Badge>
                        </div>

                        {/* Source sentence display */}
                        {item.source_sentence && (
                          <p className="text-sm italic text-muted-foreground pl-2 border-l-2 border-primary/30">
                            "{item.source_sentence}"
                          </p>
                        )}

                        <div className="text-xs text-muted-foreground">ID: {item.id}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Relationships */}
          {result.edges && result.edges.length > 0 && (
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-2xl">Relationships</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.edges.map((edge, idx) => (
                    <div key={idx} className="bg-muted/30 rounded-lg p-3 border">
                      <span className="font-semibold">{edge.source}</span>
                      {' → '}
                      <span className="font-semibold">{edge.target}</span>
                      <Badge variant="outline" className="ml-3 text-xs">
                        {edge.type}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
