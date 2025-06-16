import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import './MemoryGraph.css';
import { 
  logMemoryGraphEvent, 
  logMemoryGraphPerformance, 
  logMemoryGraphInteraction,
  logMemoryGraphFiltering,
  logMemoryGraphVisualization 
} from '../utils/memoryGraphLogger';

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
  const [hiddenTags, setHiddenTags] = useState<Set<string>>(new Set());

  // Log component initialization
  useEffect(() => {
    const initStart = performance.now();
    logMemoryGraphEvent('component_init', {
      memoriesCount: memories.length,
      hasSearchQuery: Boolean(searchQuery),
      initialHiddenTags: hiddenTags.size
    });
    logMemoryGraphPerformance('component_init', initStart, {
      memoriesCount: memories.length
    });
  }, [memories.length, searchQuery, hiddenTags.size]);

  // Color scheme for different tags
  const tagColors: { [key: string]: string } = useMemo(() => {
    const colorGenStart = performance.now();
    
    const baseColors: { [key: string]: string } = {
      identity: '#10a37f',
      family: '#ff6b6b',
      work: '#4ecdc4',
      preferences: '#45b7d1',
      memory: '#96ceb4',
      default: '#8e8ea0'
    };

    // Get all unique PRIMARY tags from memories (only tags that determine node colors)
    const allTags = new Set<string>();
    memories.forEach(memory => {
      const primaryTag = memory.tags[0] || 'default';
      allTags.add(primaryTag);
    });

    // Additional colors for dynamic tags (in a consistent order)
    const dynamicColors = [
      '#f39c12', '#e74c3c', '#9b59b6', '#3498db', '#2ecc71', 
      '#f1c40f', '#e67e22', '#1abc9c', '#34495e', '#95a5a6'
    ];

    const finalColors: { [key: string]: string } = { ...baseColors };
    
    // Sort tags alphabetically to ensure consistent color assignment
    const sortedTags = Array.from(allTags).sort();
    let colorIndex = 0;
    
    sortedTags.forEach(tag => {
      if (!finalColors[tag]) {
        finalColors[tag] = dynamicColors[colorIndex % dynamicColors.length];
        colorIndex++;
      }
    });

    logMemoryGraphPerformance('color_generation', colorGenStart, {
      totalTags: allTags.size,
      dynamicTagsAssigned: colorIndex
    });

    return finalColors;
  }, [memories]);

  // Calculate similarity between two memories (simplified)
  const calculateSimilarity = useCallback((mem1: Memory, mem2: Memory): number => {
    const similarityStart = performance.now();
    
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
    
    const result = tagSimilarity + textSimilarity;
    
    logMemoryGraphPerformance('similarity_calculation', similarityStart, {
      commonTags,
      totalTags,
      commonWords,
      similarity: result
    });
    
    return result;
  }, []);

  // Smart search function - supports multiple search terms and fuzzy matching
  const matchesSearch = useCallback((memory: Memory, query: string): boolean => {
    if (!query.trim()) return true;
    
    const searchStart = performance.now();
    
    const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
    const searchableText = [
      memory.question.toLowerCase(),
      memory.answer.toLowerCase(), 
      ...memory.tags.map(tag => tag.toLowerCase()),
      memory.importance.toLowerCase()
    ].join(' ');
    
    let result = true;
    
    // Support for exact phrases (quoted search)
    if (query.includes('"')) {
      const exactPhrase = query.match(/"([^"]+)"/)?.[1];
      if (exactPhrase) {
        result = searchableText.includes(exactPhrase.toLowerCase());
      }
    } else {
      // All search terms must be found (AND logic)
      result = searchTerms.every(term => searchableText.includes(term));
    }
    
    logMemoryGraphPerformance('search_match', searchStart, {
      queryLength: query.length,
      searchTerms: searchTerms.length,
      matched: result
    });
    
    return result;
  }, []);

  // Filter memories based on search query AND hidden PRIMARY tags
  const filteredMemories = useMemo(() => {
    const filterStart = performance.now();
    let filtered = memories;
    const totalBefore = memories.length;
    
    // First filter by hidden PRIMARY tags
    if (hiddenTags.size > 0) {
      filtered = filtered.filter(memory => {
        const primaryTag = memory.tags[0] || 'default';
        return !hiddenTags.has(primaryTag);
      });
    }
    
    // Then filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(memory => matchesSearch(memory, searchQuery));
    }
    
    const totalAfter = filtered.length;
    
    logMemoryGraphFiltering('memory_filter', {
      searchQuery,
      hiddenTagsCount: hiddenTags.size,
      hiddenTags: Array.from(hiddenTags)
    }, {
      totalBefore,
      totalAfter,
      filteredCount: totalAfter
    });
    
    logMemoryGraphPerformance('memory_filtering', filterStart, {
      totalBefore,
      totalAfter,
      hiddenTagsCount: hiddenTags.size
    });
    
    console.log(`Filtered memories: ${filtered.length} of ${memories.length} (hidden primary tags: ${hiddenTags.size}, search: "${searchQuery}")`);
    return filtered;
  }, [memories, searchQuery, matchesSearch, hiddenTags]);

  // Get unique PRIMARY tags from all memories and their counts
  const tagStatus = useMemo(() => {
    const tagStatusStart = performance.now();
    
    const allTags = new Set<string>();
    memories.forEach(memory => {
      const primaryTag = memory.tags[0] || 'default';
      allTags.add(primaryTag);
    });

    // Check which tags have matching memories (based on PRIMARY tag only)
    const tagCounts: { [key: string]: { total: number; visible: number; isHidden: boolean } } = {};
    
    Array.from(allTags).forEach(tag => {
      // Count memories where this tag is the PRIMARY tag
      const totalWithTag = memories.filter(memory => {
        const primaryTag = memory.tags[0] || 'default';
        return primaryTag === tag;
      }).length;
      
      const visibleWithTag = filteredMemories.filter(memory => {
        const primaryTag = memory.tags[0] || 'default';
        return primaryTag === tag;
      }).length;
      
      tagCounts[tag] = {
        total: totalWithTag,
        visible: visibleWithTag,
        isHidden: hiddenTags.has(tag)
      };
    });

    logMemoryGraphPerformance('tag_status_calculation', tagStatusStart, {
      totalTags: allTags.size,
      hiddenTags: hiddenTags.size
    });

    return tagCounts;
  }, [memories, filteredMemories, hiddenTags]);

  // Toggle tag visibility
  const toggleTag = useCallback((tag: string) => {
    const interactionStart = performance.now();
    
    console.log('Toggling tag:', tag);
    setHiddenTags(prev => {
      const newHidden = new Set(prev);
      const wasHidden = newHidden.has(tag);
      
      if (wasHidden) {
        newHidden.delete(tag);
        console.log('Showing tag:', tag);
      } else {
        newHidden.add(tag);
        console.log('Hiding tag:', tag);
      }
      
      logMemoryGraphInteraction('tag_toggle', {
        tag,
        action: wasHidden ? 'show' : 'hide',
        totalHiddenAfter: newHidden.size
      });
      
      logMemoryGraphPerformance('tag_toggle', interactionStart, {
        tag,
        wasHidden,
        newHiddenCount: newHidden.size
      });
      
      console.log('New hidden tags:', Array.from(newHidden));
      return newHidden;
    });
  }, []);

  // Select all tags (show all)
  const selectAll = useCallback(() => {
    const interactionStart = performance.now();
    
    logMemoryGraphInteraction('select_all', {
      previousHiddenCount: hiddenTags.size,
      previousHiddenTags: Array.from(hiddenTags)
    });
    
    setHiddenTags(new Set());
    
    logMemoryGraphPerformance('select_all', interactionStart, {
      clearedTagsCount: hiddenTags.size
    });
  }, [hiddenTags]);

  // Select none (hide all)
  const selectNone = useCallback(() => {
    const interactionStart = performance.now();
    
    // Get all PRIMARY tags from memories
    const allPrimaryTags = new Set<string>();
    memories.forEach(memory => {
      const primaryTag = memory.tags[0] || 'default';
      allPrimaryTags.add(primaryTag);
    });
    
    logMemoryGraphInteraction('select_none', {
      previousHiddenCount: hiddenTags.size,
      totalTagsToHide: allPrimaryTags.size,
      tagsToHide: Array.from(allPrimaryTags)
    });
    
    console.log('Select None - hiding all primary tags:', Array.from(allPrimaryTags));
    setHiddenTags(new Set(allPrimaryTags));
    
    logMemoryGraphPerformance('select_none', interactionStart, {
      hiddenTagsCount: allPrimaryTags.size
    });
  }, [memories, hiddenTags]);

  useEffect(() => {
    const renderStart = performance.now();
    
    console.log('MemoryGraph received memories:', memories.length);
    console.log('Filtered memories:', filteredMemories.length);
    console.log('Search query:', searchQuery);
    
    logMemoryGraphEvent('render_start', {
      totalMemories: memories.length,
      filteredMemories: filteredMemories.length,
      searchQuery,
      hiddenTagsCount: hiddenTags.size
    });
    
    if (!svgRef.current || filteredMemories.length === 0) {
      console.log('Early return: svgRef.current =', svgRef.current, 'filteredMemories.length =', filteredMemories.length);
      // Clear the SVG if no matches
      if (svgRef.current) {
        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();
      }
      
      logMemoryGraphEvent('render_skipped', {
        reason: !svgRef.current ? 'no_svg_ref' : 'no_filtered_memories',
        filteredMemoriesCount: filteredMemories.length
      });
      
      return;
    }

    const processStart = performance.now();

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

    const { nodes, links } = processMemories(filteredMemories);
    
    logMemoryGraphPerformance('memory_processing', processStart, {
      nodeCount: nodes.length,
      linkCount: links.length,
      memoryCount: filteredMemories.length
    });
    
    console.log('Processed nodes:', nodes.length);
    console.log('Processed links:', links.length);

    const simulationStart = performance.now();

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

    logMemoryGraphPerformance('d3_simulation_setup', simulationStart, {
      nodeCount: nodes.length,
      linkCount: links.length
    });

    const visualStart = performance.now();

    // Create container group
    const container = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
        logMemoryGraphInteraction('zoom', {
          scale: event.transform.k,
          translateX: event.transform.x,
          translateY: event.transform.y
        });
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
        // Highlight exact search matches within filtered results
        if (searchQuery && searchQuery.length > 2) {
          const exactMatch = d.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            d.answer.toLowerCase().includes(searchQuery.toLowerCase());
          if (exactMatch) {
            return '#ffd700'; // Gold for exact matches
          }
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
        logMemoryGraphInteraction('drag_start', {
          nodeId: d.id,
          position: { x: d.x, y: d.y }
        });
      })
      .on('drag', (event: d3.D3DragEvent<SVGCircleElement, MemoryNode, MemoryNode>, d: MemoryNode) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event: d3.D3DragEvent<SVGCircleElement, MemoryNode, MemoryNode>, d: MemoryNode) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
        logMemoryGraphInteraction('drag_end', {
          nodeId: d.id,
          finalPosition: { x: event.x, y: event.y }
        });
      });

    node.call(drag);

    // Add hover and click events
    node
      .on('mouseover', (event: MouseEvent, d: MemoryNode) => {
        logMemoryGraphInteraction('node_hover_start', {
          nodeId: d.id,
          tags: d.tags,
          importance: d.importance
        });
        
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
        logMemoryGraphInteraction('node_hover_end');
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
        
        logMemoryGraphInteraction('node_click', {
          nodeId: d.id,
          tags: d.tags,
          importance: d.importance,
          hasCallback: Boolean(onMemoryClick)
        });
        
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

    logMemoryGraphPerformance('d3_visualization_setup', visualStart, {
      nodeCount: nodes.length,
      linkCount: links.length,
      renderTime: performance.now() - visualStart
    });

    logMemoryGraphVisualization('render_complete', {
      totalRenderTime: performance.now() - renderStart,
      nodeCount: nodes.length,
      linkCount: links.length,
      simulationSetupTime: performance.now() - simulationStart,
      visualSetupTime: performance.now() - visualStart
    });

    // Cleanup
    return () => {
      simulation.stop();
      logMemoryGraphEvent('render_cleanup', {
        nodeCount: nodes.length,
        linkCount: links.length
      });
    };
  }, [filteredMemories, searchQuery, onMemoryClick, tagColors, calculateSimilarity, hiddenTags, memories.length]);

  return (
    <div className="memory-graph">
      <svg ref={svgRef} className="graph-svg" />
      
      {/* Dynamic Legend */}
      <div className="graph-legend">
        <h4>Memory Types</h4>
        
        {/* Show search results count */}
        {searchQuery && (
          <div className="search-results">
            <span className="results-count">
              {filteredMemories.length} of {memories.length} memories
            </span>
            {filteredMemories.length === 0 && (
              <div className="no-results">
                No memories found for "{searchQuery}"
              </div>
            )}
          </div>
        )}
        
        {/* Select All/None Controls */}
        <div className="tag-controls">
          <button 
            className="control-btn"
            onClick={selectAll}
            disabled={hiddenTags.size === 0}
          >
            Select All
          </button>
          <button 
            className="control-btn"
            onClick={selectNone}
            disabled={hiddenTags.size === Object.keys(tagStatus).length}
          >
            Select None
          </button>
        </div>

        {/* Clickable tag buttons - show ALL actual tags from memories */}
        {Object.entries(tagStatus).map(([tag, status]) => {
          const color = tagColors[tag] || tagColors.default;
          const isHidden = status.isHidden;
          
          return (
            <button
              key={tag}
              className={`tag-button ${isHidden ? 'tag-button-hidden' : 'tag-button-visible'}`}
              onClick={() => toggleTag(tag)}
            >
              <div 
                className="tag-button-color" 
                style={{ backgroundColor: isHidden ? '#4a4a4a' : color }}
              />
              <span className="tag-button-text">{tag}</span>
              <span className="tag-button-count">
                {status.visible}/{status.total}
              </span>
            </button>
          );
        })}
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