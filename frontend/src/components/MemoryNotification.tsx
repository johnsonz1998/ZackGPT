import React, { useState, useEffect } from 'react';

interface MemoryNotificationData {
  memory_id: string;
  message: string;
  tags: string[];
  fact?: string;
  thread_id?: string;
  question_preview: string;
}

interface MemoryNotificationProps {
  notification: MemoryNotificationData;
  onClose: () => void;
  autoHide?: boolean;
  duration?: number;
}

const MemoryNotification: React.FC<MemoryNotificationProps> = ({ 
  notification, 
  onClose, 
  autoHide = true, 
  duration = 5000 
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (autoHide) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [autoHide, duration]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose();
    }, 300); // Animation duration
  };

  if (!isVisible) return null;

  return (
    <div className={`memory-notification ${isExiting ? 'exiting' : 'entering'}`}>
      <div className="memory-notification-content">
        <div className="memory-notification-header">
          <span className="memory-icon">💭</span>
          <span className="memory-message">{notification.message}</span>
          <button 
            className="memory-notification-close"
            onClick={handleClose}
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
        
        <div className="memory-notification-body">
          <div className="memory-preview">
            <strong>From:</strong> "{notification.question_preview}"
          </div>
          
          {notification.tags && notification.tags.length > 0 && (
            <div className="memory-tags">
              <strong>Tags:</strong>
              {notification.tags.map((tag, index) => (
                <span key={index} className={`memory-tag memory-tag-${tag}`}>
                  {tag}
                </span>
              ))}
            </div>
          )}
          
          {notification.fact && (
            <div className="memory-fact">
              <strong>Fact:</strong> {notification.fact}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MemoryNotification; 