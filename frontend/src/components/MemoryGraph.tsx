import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import './MemoryGraph.css';

interface Memory {
  id: string;
  question: string;
  answer: string;
  tags: string[];
  importance: 'high' | 'medium' | 'low';
  timestamp: string;
  similarity?: number;
}

interface MemoryNode extends d3.SimulationNodeDatum {
  id: string;
  question: string;
  answer: string;
  tags: string[];
  importance: 'high' | 'medium' | 'low';
  timestamp: string;
  radius: number;
  color: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface MemoryLink extends d3.SimulationLinkDatum<MemoryNode> {
  source: string | MemoryNode;
  target: string | MemoryNode;
  strength: number;
}

interface MemoryGraphProps {
  memories: Memory[];
  onMemoryClick?: (memory: Memory) => void;
  searchQuery?: string;
}

const MemoryGraph: React.FC<MemoryGraphProps> = ({ 
  memories, 
  onMemoryClick, 
  searchQuery = '' 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [, setSelectedMemory] = useState<Memory | null>(null);
  const [hoveredMemory, setHoveredMemory] = useState<Memory | null>(null);

  // Color scheme for different tags
  const tagColors: { [key: string]: string } = useMemo(() => ({
    identity: '#10a37f',
    family: '#ff6b6b',
    work: '#4ecdc4',
    preferences: '#45b7d1',
    memory: '#96ceb4',
    default: '#8e8ea0'
  }), []);

  // Calculate similarity between two memories (simplified)
  const calculateSimilarity = useCallback((mem1: Memory, mem2: Memory): number => {
    const commonTags = mem1.tags.filter(tag => mem2.tags.includes(tag)).length;
    const totalTags = new Set([...mem1.tags, ...mem2.tags]).size;
    
    // Simple similarity based on shared tags and text overlap
    const tagSimilarity = totalTags > 0 ? commonTags / totalTags : 0;
    
    // Add text similarity (very basic)
    const text1 = (mem1.question + ' ' + mem1.answer).toLowerCase();
    const text2 = (mem2.question + ' ' + mem2.answer).toLowerCase();
    const words1 = text1.split(' ');
    const words2 = text2.split(' ');
    const commonWords = words1.filter(word => words2.includes(word) && word.length > 3).length;
    const textSimilarity = Math.min(commonWords / Math.max(words1.length, words2.length), 0.5);
    
    return tagSimilarity + textSimilarity;
  }, []);

  useEffect(() => {
    console.log('MemoryGraph received memories:', memories);
    console.log('Memory count:', memories.length);
    
    if (!svgRef.current || memories.length === 0) {
      console.log('Early return: svgRef.current =', svgRef.current, 'memories.length =', memories.length);
      return;
    }

    // Process memories into nodes and links
    const processMemories = (memories: Memory[]) => {
      const nodes: MemoryNode[] = memories.map(memory => {
        const primaryTag = memory.tags[0] || 'default';
        const radius = memory.importance === 'high' ? 12 : memory.importance === 'medium' ? 8 : 6;
        
        return {
          id: memory.id,
          question: memory.question,
          answer: memory.answer,
          tags: memory.tags,
          importance: memory.importance,
          timestamp: memory.timestamp,
          radius,
          color: tagColors[primaryTag] || tagColors.default
        };
      });

      const links: MemoryLink[] = [];
      
      // Create links between similar memories
      for (let i = 0; i < memories.length; i++) {
        for (let j = i + 1; j < memories.length; j++) {
          const similarity = calculateSimilarity(memories[i], memories[j]);
          
          if (similarity > 0.2) { // Threshold for creating a link
            links.push({
              source: memories[i].id,
              target: memories[j].id,
              strength: similarity
            });
          }
        }
      }

      return { nodes, links };
    };

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous render

    const width = 800;
    const height = 600;
    
    svg.attr('width', width).attr('height', height);

    const { nodes, links } = processMemories(memories);
    console.log('Processed nodes:', nodes);
    console.log('Processed links:', links);

    // Create simulation
    const simulation = d3.forceSimulation<MemoryNode>(nodes)
      .force('link', d3.forceLink<MemoryNode, MemoryLink>(links)
        .id((d: MemoryNode) => d.id)
        .distance((d: MemoryLink) => 50 + (1 - d.strength) * 100)
        .strength((d: MemoryLink) => d.strength * 0.5)
      )
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: d3.SimulationNodeDatum) => (d as MemoryNode).radius + 2));

    // Create container group
    const container = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    // Create links
    const link = container.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#565869')
      .attr('stroke-opacity', (d: MemoryLink) => d.strength * 0.6)
      .attr('stroke-width', (d: MemoryLink) => Math.max(1, d.strength * 3));
      
    console.log('Created links:', link.size());

    // Create nodes
    const node = container.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', (d: MemoryNode) => d.radius)
      .attr('fill', (d: MemoryNode) => {
        // Highlight if matches search
        if (searchQuery && (
          d.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
        )) {
          return '#ffd700'; // Gold for search matches
        }
        return d.color;
      })
      .attr('stroke', '#2f2f2f')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');
      
    console.log('Created nodes:', node.size());

    // Add labels
    const labels = container.append('g')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text((d: MemoryNode) => d.question.slice(0, 20) + (d.question.length > 20 ? '...' : ''))
      .attr('font-size', '10px')
      .attr('fill', '#ececec')
      .attr('text-anchor', 'middle')
      .attr('dy', (d: MemoryNode) => d.radius + 15)
      .style('pointer-events', 'none');

    // Initialize nodes at center temporarily (so we can see them immediately)
    node
      .attr('cx', width / 2)
      .attr('cy', height / 2);
      
    labels
      .attr('x', width / 2)
      .attr('y', height / 2);

    // Add drag behavior
    const drag = d3.drag<SVGCircleElement, MemoryNode>()
      .on('start', (event: d3.D3DragEvent<SVGCircleElement, MemoryNode, MemoryNode>, d: MemoryNode) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event: d3.D3DragEvent<SVGCircleElement, MemoryNode, MemoryNode>, d: MemoryNode) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event: d3.D3DragEvent<SVGCircleElement, MemoryNode, MemoryNode>, d: MemoryNode) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });

    node.call(drag);

    // Add hover and click events
    node
      .on('mouseover', (event: MouseEvent, d: MemoryNode) => {
        setHoveredMemory({
          id: d.id,
          question: d.question,
          answer: d.answer,
          tags: d.tags,
          importance: d.importance,
          timestamp: d.timestamp
        });
      })
      .on('mouseout', () => {
        setHoveredMemory(null);
      })
      .on('click', (event: MouseEvent, d: MemoryNode) => {
        const memory = {
          id: d.id,
          question: d.question,
          answer: d.answer,
          tags: d.tags,
          importance: d.importance,
          timestamp: d.timestamp
        };
        setSelectedMemory(memory);
        onMemoryClick?.(memory);
      });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: MemoryLink) => (d.source as MemoryNode).x!)
        .attr('y1', (d: MemoryLink) => (d.source as MemoryNode).y!)
        .attr('x2', (d: MemoryLink) => (d.target as MemoryNode).x!)
        .attr('y2', (d: MemoryLink) => (d.target as MemoryNode).y!);

      node
        .attr('cx', (d: MemoryNode) => d.x!)
        .attr('cy', (d: MemoryNode) => d.y!);

      labels
        .attr('x', (d: MemoryNode) => d.x!)
        .attr('y', (d: MemoryNode) => d.y!);
    });

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [memories, searchQuery, onMemoryClick, tagColors, calculateSimilarity]);

  return (
    <div className="memory-graph">
      <svg ref={svgRef} className="graph-svg" />
      
      {/* Legend */}
      <div className="graph-legend">
        <h4>Legend</h4>
        {Object.entries(tagColors).map(([tag, color]) => (
          <div key={tag} className="legend-item">
            <div 
              className="legend-color" 
              style={{ backgroundColor: color }}
            />
            <span>{tag}</span>
          </div>
        ))}
      </div>

      {/* Tooltip */}
      {hoveredMemory && (
        <div className="memory-tooltip">
          <h4>{hoveredMemory.question}</h4>
          <p>{hoveredMemory.answer.slice(0, 100)}...</p>
          <div className="tooltip-tags">
            {hoveredMemory.tags.map(tag => (
              <span key={tag} className="tooltip-tag">{tag}</span>
            ))}
          </div>
          <div className="tooltip-importance">
            Importance: {hoveredMemory.importance}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="graph-controls">
        <div className="control-hint">
          💡 Drag nodes • Zoom with mouse wheel • Click to select
        </div>
      </div>
    </div>
  );
};

export default MemoryGraph; 