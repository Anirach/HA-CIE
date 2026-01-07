/**
 * Causal Graph page component.
 * Shows interactive knowledge graph visualization using Cytoscape.js.
 * Includes Timeline Mode for animated assessment history visualization.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape';
import {
  GitBranch,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RefreshCw,
  X,
  ArrowRight,
  AlertTriangle,
  Shield,
  CheckCircle2,
  Info,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronRight,
  ChevronLeft,
} from 'lucide-react';
import { getStandardsGraph, getChapterDetail, getRelationshipDetail } from '../api/graph';
import { getSnapshots, getSnapshot } from '../api/timeline';
import type { ChapterDetail, RelationshipDetail, GraphNodeData, GraphEdgeData } from '../types/graph';
import type { SnapshotSummary, SnapshotDetail } from '../types/timeline';

// Part colors
const PART_COLORS: Record<string, string> = {
  I: '#9333ea',   // Purple
  II: '#dc2626',  // Red
  III: '#16a34a', // Green
  IV: '#2563eb',  // Blue
};

const PART_NAMES: Record<string, string> = {
  I: 'Organization Management',
  II: 'Hospital Systems',
  III: 'Patient Care',
  IV: 'Results',
};

// Score to color mapping
const getScoreColor = (score: number): string => {
  if (score >= 4.0) return '#16a34a'; // Green
  if (score >= 3.0) return '#eab308'; // Yellow
  if (score >= 2.0) return '#f97316'; // Orange
  return '#dc2626'; // Red
};

// Cytoscape layout options
const LAYOUT_OPTIONS = {
  name: 'cose',
  idealEdgeLength: 150,
  nodeOverlap: 20,
  refresh: 20,
  fit: true,
  padding: 50,
  randomize: false,
  componentSpacing: 100,
  nodeRepulsion: 8000,
  edgeElasticity: 100,
  nestingFactor: 5,
  gravity: 80,
  numIter: 1000,
  initialTemp: 200,
  coolingFactor: 0.95,
  minTemp: 1.0,
};

// Cytoscape style
const CYTOSCAPE_STYLE: cytoscape.Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'background-color': 'data(color)',
      'label': 'data(label)',
      'text-wrap': 'wrap',
      'text-max-width': '100px',
      'font-size': '11px',
      'text-valign': 'center',
      'text-halign': 'center',
      'width': 80,
      'height': 80,
      'border-width': 3,
      'border-color': '#ffffff',
      'color': '#ffffff',
      'text-outline-width': 2,
      'text-outline-color': 'data(color)',
      'transition-property': 'background-color, border-color, width, height',
      'transition-duration': 400,
    },
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#fbbf24',
      'width': 90,
      'height': 90,
    },
  },
  {
    selector: 'node.highlighted',
    style: {
      'border-width': 4,
      'border-color': '#fbbf24',
    },
  },
  {
    selector: 'node.faded',
    style: {
      'opacity': 0.3,
    },
  },
  {
    selector: 'node.improved',
    style: {
      'border-width': 4,
      'border-color': '#16a34a',
    },
  },
  {
    selector: 'node.declined',
    style: {
      'border-width': 4,
      'border-color': '#dc2626',
    },
  },
  {
    selector: 'edge',
    style: {
      'width': 'data(width)',
      'line-color': '#94a3b8',
      'target-arrow-color': '#94a3b8',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'opacity': 0.7,
    },
  },
  {
    selector: 'edge:selected',
    style: {
      'line-color': '#fbbf24',
      'target-arrow-color': '#fbbf24',
      'opacity': 1,
      'width': 'mapData(strength, 0, 1, 3, 8)',
    },
  },
  {
    selector: 'edge.highlighted',
    style: {
      'line-color': '#fbbf24',
      'target-arrow-color': '#fbbf24',
      'opacity': 1,
    },
  },
  {
    selector: 'edge.faded',
    style: {
      'opacity': 0.15,
    },
  },
];

// Playback speed options
const SPEED_OPTIONS = [
  { label: '0.5x', value: 0.5 },
  { label: '1x', value: 1 },
  { label: '2x', value: 2 },
  { label: '4x', value: 4 },
];

export function GraphPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Basic state
  const [selectedPart, setSelectedPart] = useState<string>('all');
  const [selectedNode, setSelectedNode] = useState<GraphNodeData | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdgeData | null>(null);
  const [chapterDetail, setChapterDetail] = useState<ChapterDetail | null>(null);
  const [relationshipDetail, setRelationshipDetail] = useState<RelationshipDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  // Timeline state
  const [isTimelineMode, setIsTimelineMode] = useState(false);
  const [snapshots, setSnapshots] = useState<SnapshotSummary[]>([]);
  const [currentSnapshotIndex, setCurrentSnapshotIndex] = useState(0);
  const [currentSnapshot, setCurrentSnapshot] = useState<SnapshotDetail | null>(null);
  const [previousSnapshot, setPreviousSnapshot] = useState<SnapshotDetail | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [showChangesPanel, setShowChangesPanel] = useState(true);

  // Fetch graph data
  const { data: graphData, isLoading, error, refetch } = useQuery({
    queryKey: ['standards-graph'],
    queryFn: getStandardsGraph,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch timeline snapshots
  const { data: timelineData } = useQuery({
    queryKey: ['timeline-snapshots'],
    queryFn: getSnapshots,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (timelineData?.snapshots) {
      setSnapshots(timelineData.snapshots);
    }
  }, [timelineData]);

  // Load current snapshot when timeline mode is active
  useEffect(() => {
    if (isTimelineMode && snapshots.length > 0) {
      loadSnapshot(currentSnapshotIndex);
    }
  }, [isTimelineMode, currentSnapshotIndex, snapshots]);

  const loadSnapshot = async (index: number) => {
    try {
      const snapshot = await getSnapshot(index);
      setPreviousSnapshot(currentSnapshot);
      setCurrentSnapshot(snapshot);
      
      // Update node colors based on scores
      if (cyRef.current && snapshot) {
        updateNodeColors(snapshot);
      }
    } catch (err) {
      console.error('Failed to load snapshot:', err);
    }
  };

  const updateNodeColors = (snapshot: SnapshotDetail) => {
    if (!cyRef.current) return;
    
    const cy = cyRef.current;
    
    cy.nodes().forEach((node) => {
      const nodeData = node.data() as GraphNodeData;
      const score = snapshot.scores[nodeData.id];
      
      if (score !== undefined) {
        const color = getScoreColor(score);
        node.style('background-color', color);
        node.style('text-outline-color', color);
        
        // Find if this chapter had a change
        const change = snapshot.changes.find((c) => c.chapter_id === nodeData.id);
        node.removeClass('improved declined');
        
        if (change) {
          if (change.change > 0.1) {
            node.addClass('improved');
          } else if (change.change < -0.1) {
            node.addClass('declined');
          }
        }
      }
    });
  };

  const resetNodeColors = () => {
    if (!cyRef.current || !graphData) return;
    
    const cy = cyRef.current;
    cy.nodes().forEach((node) => {
      const nodeData = node.data() as GraphNodeData;
      node.style('background-color', nodeData.color);
      node.style('text-outline-color', nodeData.color);
      node.removeClass('improved declined');
    });
  };

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Create new instance
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...graphData.nodes.map((n) => ({ data: n.data })),
        ...graphData.edges.map((e) => ({ data: e.data })),
      ],
      style: CYTOSCAPE_STYLE,
      layout: LAYOUT_OPTIONS,
      minZoom: 0.3,
      maxZoom: 3,
    });

    // Node click handler
    cy.on('tap', 'node', async (evt) => {
      const node = evt.target as NodeSingular;
      const nodeData = node.data() as GraphNodeData;
      
      setSelectedNode(nodeData);
      setSelectedEdge(null);
      setRelationshipDetail(null);
      
      // Highlight connected nodes and edges
      cy.elements().removeClass('highlighted faded');
      const connectedEdges = node.connectedEdges();
      const connectedNodes = connectedEdges.connectedNodes();
      
      cy.elements().not(node).not(connectedEdges).not(connectedNodes).addClass('faded');
      connectedEdges.addClass('highlighted');
      connectedNodes.addClass('highlighted');
      
      // Fetch chapter detail
      setIsLoadingDetail(true);
      try {
        const detail = await getChapterDetail(nodeData.id);
        setChapterDetail(detail);
      } catch (err) {
        console.error('Failed to fetch chapter detail:', err);
      } finally {
        setIsLoadingDetail(false);
      }
    });

    // Edge click handler
    cy.on('tap', 'edge', async (evt) => {
      const edge = evt.target as EdgeSingular;
      const edgeData = edge.data() as GraphEdgeData;
      
      setSelectedEdge(edgeData);
      setSelectedNode(null);
      setChapterDetail(null);
      
      // Highlight the edge and connected nodes
      cy.elements().removeClass('highlighted faded');
      cy.elements().not(edge).not(edge.connectedNodes()).addClass('faded');
      edge.addClass('highlighted');
      edge.connectedNodes().addClass('highlighted');
      
      // Fetch relationship detail
      setIsLoadingDetail(true);
      try {
        const detail = await getRelationshipDetail(edgeData.source, edgeData.target);
        setRelationshipDetail(detail);
      } catch (err) {
        console.error('Failed to fetch relationship detail:', err);
      } finally {
        setIsLoadingDetail(false);
      }
    });

    // Background click handler
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted faded');
        setSelectedNode(null);
        setSelectedEdge(null);
        setChapterDetail(null);
        setRelationshipDetail(null);
      }
    });

    cyRef.current = cy;

    return () => {
      // Stop any running layouts before destroying
      cy.stop();
      cyRef.current = null;
      cy.destroy();
    };
  }, [graphData]);

  // Filter nodes by part
  useEffect(() => {
    if (!cyRef.current) return;
    
    const cy = cyRef.current;
    
    if (selectedPart === 'all') {
      cy.elements().show();
    } else {
      cy.nodes().forEach((node) => {
        const nodeData = node.data() as GraphNodeData;
        if (nodeData.part === selectedPart) {
          node.show();
        } else {
          node.hide();
        }
      });
      cy.edges().forEach((edge) => {
        const source = edge.source();
        const target = edge.target();
        if (source.visible() && target.visible()) {
          edge.show();
        } else {
          edge.hide();
        }
      });
    }
    
    // Re-layout if filter changed
    if (selectedPart !== 'all' && cyRef.current) {
      const layout = cy.layout({ ...LAYOUT_OPTIONS, animate: true, animationDuration: 500 });
      layout.run();
    }
  }, [selectedPart]);

  // Playback control
  useEffect(() => {
    if (isPlaying && snapshots.length > 0) {
      const interval = 2000 / playbackSpeed; // Base interval is 2 seconds
      
      playIntervalRef.current = setInterval(() => {
        setCurrentSnapshotIndex((prev) => {
          if (prev >= snapshots.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, interval);
    } else {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
        playIntervalRef.current = null;
      }
    }

    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, snapshots.length]);

  // Toggle timeline mode
  const toggleTimelineMode = useCallback(() => {
    setIsTimelineMode((prev) => {
      if (prev) {
        // Exiting timeline mode - reset colors
        resetNodeColors();
        setIsPlaying(false);
      }
      return !prev;
    });
  }, []);

  // Playback controls
  const handlePlay = useCallback(() => setIsPlaying(true), []);
  const handlePause = useCallback(() => setIsPlaying(false), []);
  const handlePrevious = useCallback(() => {
    setIsPlaying(false);
    setCurrentSnapshotIndex((prev) => Math.max(0, prev - 1));
  }, []);
  const handleNext = useCallback(() => {
    setIsPlaying(false);
    setCurrentSnapshotIndex((prev) => Math.min(snapshots.length - 1, prev + 1));
  }, [snapshots.length]);
  const handleReset = useCallback(() => {
    setIsPlaying(false);
    setCurrentSnapshotIndex(0);
  }, []);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.3);
  }, []);

  const handleZoomOut = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() * 0.7);
  }, []);

  const handleFit = useCallback(() => {
    cyRef.current?.fit(undefined, 50);
  }, []);

  const handleReLayout = useCallback(() => {
    cyRef.current?.layout(LAYOUT_OPTIONS).run();
  }, []);

  const closeDetailPanel = useCallback(() => {
    setSelectedNode(null);
    setSelectedEdge(null);
    setChapterDetail(null);
    setRelationshipDetail(null);
    cyRef.current?.elements().removeClass('highlighted faded');
  }, []);

  // Render criterion category badge
  const renderCategoryBadge = (category: string) => {
    const styles: Record<string, string> = {
      essential: 'bg-red-100 text-red-800',
      core: 'bg-amber-100 text-amber-800',
      basic: 'bg-gray-100 text-gray-800',
    };
    const icons: Record<string, React.ReactNode> = {
      essential: <AlertTriangle className="h-3 w-3 mr-1" />,
      core: <Shield className="h-3 w-3 mr-1" />,
      basic: <CheckCircle2 className="h-3 w-3 mr-1" />,
    };
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${styles[category]}`}>
        {icons[category]}
        {category.charAt(0).toUpperCase() + category.slice(1)}
      </span>
    );
  };

  // Render strength indicator
  const renderStrengthBar = (strength: number) => {
    const percentage = strength * 100;
    const color = strength >= 0.8 ? 'bg-green-500' : strength >= 0.6 ? 'bg-amber-500' : 'bg-red-500';
    return (
      <div className="flex items-center gap-2">
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className={`h-full ${color}`} style={{ width: `${percentage}%` }} />
        </div>
        <span className="text-sm font-medium text-gray-700">{(strength * 100).toFixed(0)}%</span>
      </div>
    );
  };

  // Render change indicator
  const renderChangeIndicator = (change: number) => {
    if (change > 0.1) {
      return (
        <span className="inline-flex items-center gap-1 text-green-600">
          <TrendingUp className="h-3 w-3" />
          +{change.toFixed(2)}
        </span>
      );
    }
    if (change < -0.1) {
      return (
        <span className="inline-flex items-center gap-1 text-red-600">
          <TrendingDown className="h-3 w-3" />
          {change.toFixed(2)}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-gray-400">
        <Minus className="h-3 w-3" />
        {change.toFixed(2)}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading graph data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load graph</h3>
          <p className="text-gray-500 mb-4">Please try again later</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Page Header */}
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Causal Knowledge Graph</h1>
          <p className="mt-1 text-gray-600">
            {isTimelineMode
              ? 'Viewing assessment history over time'
              : 'Explore cause-effect relationships between HA Thailand Standard criteria'}
          </p>
        </div>
        
        {/* Timeline Mode Toggle */}
        <button
          onClick={toggleTimelineMode}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            isTimelineMode
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Clock className="h-4 w-4" />
          <span className="font-medium">Timeline Mode</span>
        </button>
      </div>

      {/* Controls Bar */}
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1">
          <button
            onClick={handleZoomIn}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4 text-gray-600" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4 text-gray-600" />
          </button>
          <button
            onClick={handleFit}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            title="Fit to View"
          >
            <Maximize2 className="h-4 w-4 text-gray-600" />
          </button>
          <button
            onClick={handleReLayout}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            title="Re-layout"
          >
            <RefreshCw className="h-4 w-4 text-gray-600" />
          </button>
        </div>

        {/* Timeline Controls (visible only in timeline mode) */}
        {isTimelineMode && snapshots.length > 0 && (
          <>
            {/* Playback Controls */}
            <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1">
              <button
                onClick={handleReset}
                className="p-2 hover:bg-gray-100 rounded-md transition-colors"
                title="Reset to Start"
              >
                <SkipBack className="h-4 w-4 text-gray-600" />
              </button>
              <button
                onClick={handlePrevious}
                disabled={currentSnapshotIndex === 0}
                className="p-2 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-40"
                title="Previous"
              >
                <ChevronLeft className="h-4 w-4 text-gray-600" />
              </button>
              {isPlaying ? (
                <button
                  onClick={handlePause}
                  className="p-2 hover:bg-gray-100 rounded-md transition-colors bg-indigo-100"
                  title="Pause"
                >
                  <Pause className="h-4 w-4 text-indigo-600" />
                </button>
              ) : (
                <button
                  onClick={handlePlay}
                  disabled={currentSnapshotIndex >= snapshots.length - 1}
                  className="p-2 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-40"
                  title="Play"
                >
                  <Play className="h-4 w-4 text-gray-600" />
                </button>
              )}
              <button
                onClick={handleNext}
                disabled={currentSnapshotIndex >= snapshots.length - 1}
                className="p-2 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-40"
                title="Next"
              >
                <ChevronRight className="h-4 w-4 text-gray-600" />
              </button>
              <button
                onClick={() => setCurrentSnapshotIndex(snapshots.length - 1)}
                className="p-2 hover:bg-gray-100 rounded-md transition-colors"
                title="Skip to End"
              >
                <SkipForward className="h-4 w-4 text-gray-600" />
              </button>
            </div>

            {/* Speed Control */}
            <select
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            >
              {SPEED_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>

            {/* Timeline Slider */}
            <div className="flex-1 flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-2 min-w-[300px]">
              <span className="text-xs text-gray-500 whitespace-nowrap">
                {snapshots[0]?.label || '--'}
              </span>
              <input
                type="range"
                min={0}
                max={snapshots.length - 1}
                value={currentSnapshotIndex}
                onChange={(e) => {
                  setIsPlaying(false);
                  setCurrentSnapshotIndex(Number(e.target.value));
                }}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <span className="text-xs text-gray-500 whitespace-nowrap">
                {snapshots[snapshots.length - 1]?.label || '--'}
              </span>
            </div>

            {/* Current Date Display */}
            {currentSnapshot && (
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg px-3 py-2">
                <p className="text-sm font-medium text-indigo-900">
                  {currentSnapshot.label}
                </p>
                <p className="text-xs text-indigo-600">
                  Score: {currentSnapshot.overall_score.toFixed(2)} • {currentSnapshot.accreditation_level}
                </p>
              </div>
            )}
          </>
        )}

        <div className="flex-1" />

        {/* Domain Filter (hidden in timeline mode) */}
        {!isTimelineMode && (
          <select
            value={selectedPart}
            onChange={(e) => setSelectedPart(e.target.value)}
            className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="all">All Domains</option>
            <option value="I">Part I - Organization Management</option>
            <option value="II">Part II - Hospital Systems</option>
            <option value="III">Part III - Patient Care</option>
            <option value="IV">Part IV - Results</option>
          </select>
        )}

        {/* Legend */}
        {!isTimelineMode ? (
          <div className="hidden lg:flex items-center gap-3 px-3 py-1 bg-white border border-gray-200 rounded-lg text-xs">
            {Object.entries(PART_COLORS).map(([part, color]) => (
              <div key={part} className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-gray-600">{PART_NAMES[part]}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="hidden lg:flex items-center gap-3 px-3 py-1 bg-white border border-gray-200 rounded-lg text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-gray-600">≥4.0</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="text-gray-600">3.0-3.9</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-gray-600">2.0-2.9</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-gray-600">&lt;2.0</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Graph Container */}
        <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div ref={containerRef} className="w-full h-full min-h-[500px]" />
        </div>

        {/* Detail Panel / Changes Panel */}
        {isTimelineMode && showChangesPanel && currentSnapshot ? (
          /* Changes Panel for Timeline Mode */
          <div className="w-80 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
            <div className="px-4 py-3 border-b border-gray-100 bg-indigo-50 flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">Changes</h3>
                <p className="text-xs text-gray-600">{currentSnapshot.label}</p>
              </div>
              <button
                onClick={() => setShowChangesPanel(false)}
                className="p-1 hover:bg-indigo-100 rounded-md transition-colors"
              >
                <X className="h-4 w-4 text-gray-500" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="bg-green-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-bold text-green-700">{currentSnapshot.summary.improved}</p>
                  <p className="text-xs text-green-600">Improved</p>
                </div>
                <div className="bg-red-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-bold text-red-700">{currentSnapshot.summary.declined}</p>
                  <p className="text-xs text-red-600">Declined</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-bold text-gray-700">{currentSnapshot.summary.unchanged}</p>
                  <p className="text-xs text-gray-600">Unchanged</p>
                </div>
              </div>

              {/* Changes List */}
              {currentSnapshot.changes.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    Notable Changes
                  </p>
                  {currentSnapshot.changes.map((change) => (
                    <div
                      key={change.chapter_id}
                      className={`p-3 rounded-lg border ${
                        change.change > 0 ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span
                          className="font-medium text-sm"
                          style={{ color: PART_COLORS[change.part] }}
                        >
                          {change.chapter_id}
                        </span>
                        {renderChangeIndicator(change.change)}
                      </div>
                      <p className="text-xs text-gray-600 truncate">{change.chapter_name}</p>
                      <div className="flex items-center gap-2 mt-1 text-xs">
                        <span className="text-gray-500">{change.previous_score.toFixed(2)}</span>
                        <ArrowRight className="h-3 w-3 text-gray-400" />
                        <span className={change.change > 0 ? 'text-green-700 font-medium' : 'text-red-700 font-medium'}>
                          {change.new_score.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No significant changes in this period</p>
                </div>
              )}
            </div>
          </div>
        ) : (selectedNode || selectedEdge) ? (
          /* Regular Detail Panel */
          <div className="w-80 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
            {/* Panel Header */}
            <div
              className="px-4 py-3 border-b border-gray-100 flex items-center justify-between"
              style={{
                backgroundColor: selectedNode
                  ? `${selectedNode.color}15`
                  : selectedEdge
                  ? '#fef3c715'
                  : undefined,
              }}
            >
              <h3 className="font-semibold text-gray-900">
                {selectedNode ? selectedNode.id : selectedEdge ? 'Relationship' : ''}
              </h3>
              <button
                onClick={closeDetailPanel}
                className="p-1 hover:bg-gray-200 rounded-md transition-colors"
              >
                <X className="h-4 w-4 text-gray-500" />
              </button>
            </div>

            {/* Panel Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {isLoadingDetail ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 text-indigo-600 animate-spin" />
                </div>
              ) : selectedNode && chapterDetail ? (
                <div className="space-y-4">
                  {/* Chapter Name */}
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{chapterDetail.name}</h4>
                    <p className="text-sm text-gray-500 mt-1">
                      Part {chapterDetail.part_number} - {chapterDetail.part_name}
                    </p>
                  </div>

                  {/* Current Score in Timeline Mode */}
                  {isTimelineMode && currentSnapshot && (
                    <div className="bg-indigo-50 rounded-lg p-3">
                      <p className="text-xs font-medium text-indigo-600 mb-1">Current Score</p>
                      <p className="text-2xl font-bold text-indigo-900">
                        {currentSnapshot.scores[chapterDetail.id]?.toFixed(2) || '--'}
                      </p>
                    </div>
                  )}

                  {/* Focus */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Focus Area</p>
                    <p className="text-sm text-gray-600">{chapterDetail.focus}</p>
                  </div>

                  {/* Weight */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Weight in Part</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full"
                          style={{
                            width: `${chapterDetail.weight * 100}%`,
                            backgroundColor: chapterDetail.color,
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {(chapterDetail.weight * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  {/* Criteria Summary */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Criteria ({chapterDetail.criteria.length})</p>
                    <div className="flex gap-2 flex-wrap">
                      {renderCategoryBadge('essential')}
                      <span className="text-xs text-gray-500">
                        {chapterDetail.criteria.filter((c) => c.category === 'essential').length}
                      </span>
                      {renderCategoryBadge('core')}
                      <span className="text-xs text-gray-500">
                        {chapterDetail.criteria.filter((c) => c.category === 'core').length}
                      </span>
                      {renderCategoryBadge('basic')}
                      <span className="text-xs text-gray-500">
                        {chapterDetail.criteria.filter((c) => c.category === 'basic').length}
                      </span>
                    </div>
                  </div>

                  {/* Criteria List */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">All Criteria</p>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {chapterDetail.criteria.map((criterion) => (
                        <div
                          key={criterion.id}
                          className="p-2 bg-gray-50 rounded-lg text-sm"
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-gray-900">{criterion.id}</span>
                            {renderCategoryBadge(criterion.category)}
                          </div>
                          <p className="text-gray-600 text-xs">{criterion.name}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Relationships */}
                  {(chapterDetail.incoming_relationships.length > 0 ||
                    chapterDetail.outgoing_relationships.length > 0) && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Relationships</p>
                      
                      {chapterDetail.incoming_relationships.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs text-gray-500 mb-1">Incoming ({chapterDetail.incoming_relationships.length})</p>
                          <div className="space-y-1">
                            {chapterDetail.incoming_relationships.slice(0, 3).map((rel) => (
                              <div
                                key={`in-${rel.source}`}
                                className="flex items-center gap-2 text-xs text-gray-600"
                              >
                                <span className="font-medium" style={{ color: PART_COLORS[rel.source.split('-')[0]] }}>
                                  {rel.source}
                                </span>
                                <ArrowRight className="h-3 w-3" />
                                <span className="truncate flex-1">{chapterDetail.id}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {chapterDetail.outgoing_relationships.length > 0 && (
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Outgoing ({chapterDetail.outgoing_relationships.length})</p>
                          <div className="space-y-1">
                            {chapterDetail.outgoing_relationships.slice(0, 3).map((rel) => (
                              <div
                                key={`out-${rel.target}`}
                                className="flex items-center gap-2 text-xs text-gray-600"
                              >
                                <span className="font-medium">{chapterDetail.id}</span>
                                <ArrowRight className="h-3 w-3" />
                                <span className="truncate flex-1" style={{ color: PART_COLORS[rel.target.split('-')[0]] }}>
                                  {rel.target}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : selectedEdge && relationshipDetail ? (
                <div className="space-y-4">
                  {/* Relationship Direction */}
                  <div className="flex items-center justify-center gap-3 py-4 bg-gray-50 rounded-lg">
                    <div className="text-center">
                      <p
                        className="text-lg font-bold"
                        style={{ color: PART_COLORS[relationshipDetail.source.split('-')[0]] }}
                      >
                        {relationshipDetail.source}
                      </p>
                      <p className="text-xs text-gray-500">{relationshipDetail.source_name}</p>
                    </div>
                    <ArrowRight className="h-6 w-6 text-gray-400" />
                    <div className="text-center">
                      <p
                        className="text-lg font-bold"
                        style={{ color: PART_COLORS[relationshipDetail.target.split('-')[0]] }}
                      >
                        {relationshipDetail.target}
                      </p>
                      <p className="text-xs text-gray-500">{relationshipDetail.target_name}</p>
                    </div>
                  </div>

                  {/* Relationship Type */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Relationship Type</p>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                      {relationshipDetail.relationship_type.replace('_', ' ')}
                    </span>
                  </div>

                  {/* Strength */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Strength</p>
                    {renderStrengthBar(relationshipDetail.strength)}
                  </div>

                  {/* Mechanism */}
                  <div>
                    <div className="flex items-center gap-1 mb-2">
                      <Info className="h-4 w-4 text-gray-400" />
                      <p className="text-sm font-medium text-gray-700">Causal Mechanism</p>
                    </div>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                      {relationshipDetail.mechanism}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Select a node or edge to view details</p>
                </div>
              )}
            </div>
          </div>
        ) : isTimelineMode && !showChangesPanel ? (
          /* Show Changes Panel Button */
          <button
            onClick={() => setShowChangesPanel(true)}
            className="absolute right-6 top-32 bg-white border border-gray-200 rounded-lg p-2 shadow-sm hover:bg-gray-50"
          >
            <ChevronLeft className="h-5 w-5 text-gray-600" />
          </button>
        ) : null}
      </div>

      {/* Mobile Legend */}
      <div className="lg:hidden flex items-center justify-center gap-4 mt-4 px-3 py-2 bg-white border border-gray-200 rounded-lg text-xs">
        {!isTimelineMode ? (
          Object.entries(PART_COLORS).map(([part, color]) => (
            <div key={part} className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-gray-600">{part}</span>
            </div>
          ))
        ) : (
          <>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-gray-600">≥4.0</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="text-gray-600">3-4</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-gray-600">2-3</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-gray-600">&lt;2</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default GraphPage;
