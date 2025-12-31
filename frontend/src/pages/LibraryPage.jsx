import { useState, useEffect } from 'react';
import { getLibraryItems, getItemDetail, deleteItems } from '../api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LibraryPage() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState('all');
  const [selectedItem, setSelectedItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    loadItems();
  }, [filter]);

  const loadItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const typeFilter = filter === 'all' ? null : filter;
      const data = await getLibraryItems(typeFilter);
      setItems(data.items);
      setTotalCount(data.total_count);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load library items');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (itemId) => {
    try {
      const detail = await getItemDetail(itemId);
      setSelectedItem(detail);
    } catch (err) {
      console.error('Failed to load item detail:', err);
    }
  };

  const toggleSelectItem = (itemId) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === items.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(items.map(item => item.item_id)));
    }
  };

  const handleDeleteClick = () => {
    if (selectedIds.size > 0) {
      setShowDeleteConfirm(true);
    }
  };

  const handleConfirmDelete = async () => {
    try {
      setIsDeleting(true);
      const idsToDelete = Array.from(selectedIds);
      const result = await deleteItems(idsToDelete);

      // Show success and reload
      alert(`${result.message}\n\nDeleted ${result.deleted_encounters} encounters and ${result.deleted_edges} relationships.`);

      // Clear selection and reload
      setSelectedIds(new Set());
      setShowDeleteConfirm(false);
      await loadItems();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete items');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg font-semibold text-muted-foreground">Loading your library...</div>
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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight">Your Learning Library</h1>
        <p className="text-muted-foreground text-lg">Browse and review everything you've learned</p>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        <Button
          variant={filter === 'all' ? 'default' : 'secondary'}
          onClick={() => setFilter('all')}
          className="font-semibold"
        >
          All ({totalCount})
        </Button>
        <Button
          variant={filter === 'word' ? 'default' : 'secondary'}
          onClick={() => setFilter('word')}
          className="font-semibold"
        >
          Words
        </Button>
        <Button
          variant={filter === 'chunk' ? 'default' : 'secondary'}
          onClick={() => setFilter('chunk')}
          className="font-semibold"
        >
          Phrases
        </Button>
        <Button
          variant={filter === 'pattern' ? 'default' : 'secondary'}
          onClick={() => setFilter('pattern')}
          className="font-semibold"
        >
          Patterns
        </Button>
      </div>

      {items.length === 0 ? (
        <Card className="border-2">
          <CardContent className="pt-10 pb-10 text-center">
            <p className="text-lg font-semibold text-muted-foreground mb-2">No items found in your library yet.</p>
            <p className="text-muted-foreground">Go to the Ingest page to add some German text!</p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Selection Toolbar */}
          <Card className="border-2 bg-muted/30">
            <CardContent className="pt-4 pb-4">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === items.length && items.length > 0}
                      onChange={toggleSelectAll}
                      className="w-4 h-4 rounded border-2 border-border cursor-pointer"
                    />
                    <span className="font-semibold">Select All</span>
                  </label>
                  {selectedIds.size > 0 && (
                    <Badge variant="secondary" className="text-sm font-semibold">
                      {selectedIds.size} item{selectedIds.size !== 1 ? 's' : ''} selected
                    </Badge>
                  )}
                </div>
                {selectedIds.size > 0 && (
                  <Button
                    variant="destructive"
                    onClick={handleDeleteClick}
                    disabled={isDeleting}
                    className="font-semibold"
                  >
                    {isDeleting ? 'Deleting...' : `Delete ${selectedIds.size} item${selectedIds.size !== 1 ? 's' : ''}`}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Items Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {items.map(item => (
              <LibraryItemCard
                key={item.item_id}
                item={item}
                onViewDetail={handleViewDetail}
                isSelected={selectedIds.has(item.item_id)}
                onToggleSelect={toggleSelectItem}
              />
            ))}
          </div>
        </>
      )}

      {/* Detail Modal */}
      {selectedItem && (
        <ItemDetailModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
        />
      )}

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <ConfirmDeleteModal
          itemCount={selectedIds.size}
          onConfirm={handleConfirmDelete}
          onCancel={handleCancelDelete}
          isDeleting={isDeleting}
        />
      )}
    </div>
  );
}

// Library Item Card Component
function LibraryItemCard({ item, onViewDetail, isSelected, onToggleSelect }) {
  const { canonical_form, english_gloss, type, cefr_level, gender, stats } = item;

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'never';
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffMins > 0) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    return 'just now';
  };

  return (
    <Card className={`border-2 transition-all ${isSelected ? 'ring-2 ring-primary bg-primary/5' : 'hover:shadow-lg'}`}>
      <CardContent className="pt-4">
        <div className="space-y-3">
          {/* Checkbox and Title Row */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => onToggleSelect(item.item_id)}
              onClick={(e) => e.stopPropagation()}
              className="w-5 h-5 mt-1 rounded border-2 border-border cursor-pointer flex-shrink-0"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="text-xl font-bold break-words">{canonical_form}</h3>
                <Badge variant="secondary" className="font-semibold flex-shrink-0">
                  {type === 'chunk' ? 'Phrase' : type.charAt(0).toUpperCase() + type.slice(1)}
                </Badge>
              </div>
              <p className="text-muted-foreground">{english_gloss || 'No translation'}</p>
              <div className="flex gap-2 mt-1 text-sm text-muted-foreground">
                {gender && <span className="font-semibold">{gender}</span>}
                {cefr_level && <span className="font-semibold">{cefr_level}</span>}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="text-sm text-muted-foreground flex items-center gap-2 flex-wrap">
            <span>👁 Seen {stats.total_encounters} times</span>
            {stats.total_encounters > 0 && (
              <>
                <span>•</span>
                <span>✓ {Math.round(stats.success_rate * 100)}%</span>
                <span>•</span>
                <span>{formatTimeAgo(stats.last_seen)}</span>
              </>
            )}
          </div>

          {/* View Details Button */}
          <Button
            onClick={() => onViewDetail(item.item_id)}
            variant="outline"
            className="w-full font-semibold"
          >
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Item Detail Modal Component
function ItemDetailModal({ item, onClose }) {
  const { canonical_form, metadata, stats, related_items, recent_encounters } = item;

  // Group related items by relation label
  const groupedRelations = related_items.reduce((acc, rel) => {
    const label = rel.relation_label;
    if (!acc[label]) acc[label] = [];
    acc[label].push(rel);
    return acc;
  }, {});

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between gap-4">
            <span className="text-3xl font-extrabold">{canonical_form}</span>
            <Badge variant="secondary" className="font-semibold text-base">
              {item.type === 'chunk' ? 'Phrase' : item.type.charAt(0).toUpperCase() + item.type.slice(1)}
            </Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Metadata Section */}
          <div className="space-y-3">
            {metadata.english_gloss && (
              <p className="text-xl text-muted-foreground italic">{metadata.english_gloss}</p>
            )}
            <div className="grid grid-cols-2 gap-3">
              {metadata.gender && (
                <div className="bg-muted/30 p-3 rounded-lg">
                  <strong className="text-sm text-muted-foreground uppercase">Gender:</strong>
                  <div className="font-semibold">{metadata.gender}</div>
                </div>
              )}
              {metadata.plural && (
                <div className="bg-muted/30 p-3 rounded-lg">
                  <strong className="text-sm text-muted-foreground uppercase">Plural:</strong>
                  <div className="font-semibold">{metadata.plural}</div>
                </div>
              )}
              {metadata.cefr_guess && (
                <div className="bg-muted/30 p-3 rounded-lg">
                  <strong className="text-sm text-muted-foreground uppercase">CEFR Level:</strong>
                  <div className="font-semibold">{metadata.cefr_guess}</div>
                </div>
              )}
              {metadata.pos_hint && (
                <div className="bg-muted/30 p-3 rounded-lg">
                  <strong className="text-sm text-muted-foreground uppercase">Part of Speech:</strong>
                  <div className="font-semibold">{metadata.pos_hint}</div>
                </div>
              )}
            </div>
            {metadata.why_worth_learning && (
              <Card className="border-2 bg-accent/20">
                <CardContent className="pt-4">
                  <strong className="text-sm text-muted-foreground uppercase">Why learn this:</strong>
                  <p className="mt-2">{metadata.why_worth_learning}</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Stats Section */}
          <div className="space-y-3">
            <h3 className="text-xl font-extrabold">Your Performance</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Card className="border-2 bg-gradient-to-br from-primary/10 to-primary/5">
                <CardContent className="pt-4 text-center">
                  <div className="text-3xl font-extrabold text-primary">{stats.total_encounters}</div>
                  <div className="text-xs text-muted-foreground uppercase font-semibold mt-1">Times Seen</div>
                </CardContent>
              </Card>
              <Card className="border-2 bg-gradient-to-br from-green-500/10 to-green-500/5">
                <CardContent className="pt-4 text-center">
                  <div className="text-3xl font-extrabold text-green-600">{stats.correct_count}</div>
                  <div className="text-xs text-muted-foreground uppercase font-semibold mt-1">Correct</div>
                </CardContent>
              </Card>
              <Card className="border-2 bg-gradient-to-br from-destructive/10 to-destructive/5">
                <CardContent className="pt-4 text-center">
                  <div className="text-3xl font-extrabold text-destructive">{stats.incorrect_count}</div>
                  <div className="text-xs text-muted-foreground uppercase font-semibold mt-1">Incorrect</div>
                </CardContent>
              </Card>
              <Card className="border-2 bg-gradient-to-br from-accent/30 to-accent/10">
                <CardContent className="pt-4 text-center">
                  <div className="text-3xl font-extrabold">{Math.round(stats.success_rate * 100)}%</div>
                  <div className="text-xs text-muted-foreground uppercase font-semibold mt-1">Success Rate</div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Relationships Section */}
          {Object.keys(groupedRelations).length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xl font-extrabold">Related Items</h3>
              {Object.entries(groupedRelations).map(([label, items]) => (
                <div key={label} className="space-y-2">
                  <h4 className="font-bold text-muted-foreground">{label}</h4>
                  <div className="flex flex-wrap gap-2">
                    {items.map(rel => (
                      <Badge key={rel.item_id} variant="outline" className="text-sm">
                        {rel.canonical_form}
                        {rel.english_gloss && <span className="text-muted-foreground"> ({rel.english_gloss})</span>}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recent Encounters */}
          {recent_encounters.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xl font-extrabold">Recent Practice</h3>
              <div className="space-y-2">
                {recent_encounters.map(enc => (
                  <div key={enc.encounter_id} className="bg-muted/20 p-3 rounded-lg border space-y-2">
                    <div className="flex items-center gap-3">
                      <span className={`text-xl font-bold ${enc.correct ? 'text-green-600' : 'text-destructive'}`}>
                        {enc.correct ? '✓' : '✗'}
                      </span>
                      <Badge variant="secondary" className="font-semibold">
                        {enc.mode}
                      </Badge>
                      <span className="text-sm text-muted-foreground ml-auto">
                        {new Date(enc.timestamp).toLocaleString()}
                      </span>
                    </div>
                    {enc.context_sentence && enc.mode === 'extract' && (
                      <p className="text-sm italic text-muted-foreground pl-8">
                        "{enc.context_sentence}"
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Confirmation Modal for Deletion
function ConfirmDeleteModal({ itemCount, onConfirm, onCancel, isDeleting }) {
  return (
    <Dialog open={true} onOpenChange={onCancel}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-2xl font-extrabold">Confirm Deletion</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p>
            Are you sure you want to delete <strong className="font-extrabold">{itemCount}</strong> item{itemCount !== 1 ? 's' : ''}?
          </p>
          <Alert variant="destructive" className="border-2">
            <AlertDescription className="font-semibold">
              This will permanently delete the item{itemCount !== 1 ? 's' : ''} along with all associated encounters and relationships. This action cannot be undone.
            </AlertDescription>
          </Alert>
        </div>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={onCancel}
            disabled={isDeleting}
            className="font-semibold"
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
            className="font-extrabold"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
