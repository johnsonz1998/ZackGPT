import React, { useState } from 'react';
import { Save, X } from 'lucide-react';
import './MemoryEditForm.css';

interface Memory {
  id: string;
  question: string;
  answer: string;
  tags: string[];
  importance: 'high' | 'medium' | 'low';
  timestamp: string;
}

interface MemoryEditFormProps {
  memory: Memory;
  onSave: (updates: Partial<Memory>) => void;
  onCancel: () => void;
}

const MemoryEditForm: React.FC<MemoryEditFormProps> = ({ memory, onSave, onCancel }) => {
  const [question, setQuestion] = useState(memory.question);
  const [answer, setAnswer] = useState(memory.answer);
  const [tags, setTags] = useState(memory.tags.join(', '));
  const [importance, setImportance] = useState(memory.importance);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    console.log('Save button clicked');
    setIsSaving(true);
    try {
      const tagsArray = tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
      const updates = {
        question: question.trim(),
        answer: answer.trim(),
        tags: tagsArray,
        importance
      };
      console.log('Sending updates:', updates);
      await onSave(updates);
      console.log('Save completed successfully');
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const isFormValid = () => {
    return question.trim().length > 0 && answer.trim().length > 0;
  };

  return (
    <div className="memory-edit-form">
      <div className="memory-edit-section">
        <label className="memory-edit-label">Question</label>
        <textarea
          className="memory-edit-textarea"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter the question..."
          rows={3}
        />
      </div>

      <div className="memory-edit-section">
        <label className="memory-edit-label">Answer</label>
        <textarea
          className="memory-edit-textarea"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Enter the answer..."
          rows={4}
        />
      </div>

      <div className="memory-edit-section">
        <label className="memory-edit-label">Tags</label>
        <input
          type="text"
          className="memory-edit-input"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="Enter tags separated by commas..."
        />
        <div className="memory-edit-hint">Separate multiple tags with commas</div>
      </div>

      <div className="memory-edit-section">
        <label className="memory-edit-label">Importance</label>
        <select
          className="memory-edit-select"
          value={importance}
          onChange={(e) => setImportance(e.target.value as 'high' | 'medium' | 'low')}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="memory-edit-actions">
        <button 
          className="memory-save-btn" 
          onClick={handleSave}
          disabled={!isFormValid() || isSaving}
        >
          <Save size={16} />
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
        <button 
          className="memory-cancel-btn" 
          onClick={onCancel}
          disabled={isSaving}
        >
          <X size={16} />
          Cancel
        </button>
      </div>
    </div>
  );
};

export default MemoryEditForm; 