import React from 'react';
import { Edit, Trash2 } from 'lucide-react';
import './MemoryDetailView.css';

interface Memory {
  id: string;
  question: string;
  answer: string;
  tags: string[];
  importance: 'high' | 'medium' | 'low';
  timestamp: string;
}

interface MemoryDetailViewProps {
  memory: Memory;
  onEdit: () => void;
  onDelete: () => void;
}

const MemoryDetailView: React.FC<MemoryDetailViewProps> = ({ memory, onEdit, onDelete }) => {
  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#27ae60';
      default: return '#8e8ea0';
    }
  };

  return (
    <div className="memory-detail-view">
      <div className="memory-detail-section">
        <label className="memory-detail-label">Question</label>
        <div className="memory-detail-content">{memory.question}</div>
      </div>

      <div className="memory-detail-section">
        <label className="memory-detail-label">Answer</label>
        <div className="memory-detail-content">{memory.answer}</div>
      </div>

      <div className="memory-detail-section">
        <label className="memory-detail-label">Tags</label>
        <div className="memory-detail-tags">
          {memory.tags.length > 0 ? (
            memory.tags.map((tag, index) => (
              <span key={index} className="memory-detail-tag">
                {tag}
              </span>
            ))
          ) : (
            <span className="memory-detail-no-tags">No tags</span>
          )}
        </div>
      </div>

      <div className="memory-detail-section">
        <label className="memory-detail-label">Importance</label>
        <div 
          className="memory-detail-importance"
          style={{ color: getImportanceColor(memory.importance) }}
        >
          {memory.importance.charAt(0).toUpperCase() + memory.importance.slice(1)}
        </div>
      </div>

      <div className="memory-detail-section">
        <label className="memory-detail-label">Created</label>
        <div className="memory-detail-timestamp">{formatDate(memory.timestamp)}</div>
      </div>

      <div className="memory-detail-actions">
        <button className="memory-edit-btn" onClick={onEdit}>
          <Edit size={16} />
          Edit Memory
        </button>
        <button className="memory-delete-btn" onClick={onDelete}>
          <Trash2 size={16} />
          Delete Memory
        </button>
      </div>
    </div>
  );
};

export default MemoryDetailView; 