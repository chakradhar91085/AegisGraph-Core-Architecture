import { useState, useCallback } from 'react';
import type { GraphVisualizationPayload, GraphNode, GraphEdge } from '../api';

export interface VisualGraphNode extends GraphNode {
  isNew: boolean;
}

export interface VisualGraphEdge extends GraphEdge {
  isNew: boolean;
}

export interface GraphState {
  nodes: VisualGraphNode[];
  edges: VisualGraphEdge[];
}

export function useGraphState() {
  const [graph, setGraph] = useState<GraphState>({ nodes: [], edges: [] });

  const addGraphData = useCallback((newData?: GraphVisualizationPayload) => {
    if (!newData || (newData.nodes.length === 0 && newData.edges.length === 0)) {
      // If a query is blocked or doesn't return graph data, we just clear the 'isNew' flag on existing nodes
      // so they become 'previously seen'.
      setGraph(prev => ({
        nodes: prev.nodes.map(n => ({ ...n, isNew: false })),
        edges: prev.edges.map(e => ({ ...e, isNew: false }))
      }));
      return;
    }

    setGraph(prev => {
      const existingNodeIds = new Set(prev.nodes.map(n => n.id));
      const existingEdgeSigs = new Set(prev.edges.map(e => `${e.source}-${e.target}-${e.type}`));

      const updatedNodes = prev.nodes.map(n => ({ ...n, isNew: false }));
      const updatedEdges = prev.edges.map(e => ({ ...e, isNew: false }));

      newData.nodes.forEach(node => {
        if (!existingNodeIds.has(node.id)) {
          updatedNodes.push({ ...node, isNew: true });
          existingNodeIds.add(node.id);
        } else {
          // If the node was returned again, we might want to highlight it again.
          const idx = updatedNodes.findIndex(n => n.id === node.id);
          if (idx !== -1) updatedNodes[idx].isNew = true;
        }
      });

      newData.edges.forEach(edge => {
        const sig = `${edge.source}-${edge.target}-${edge.type}`;
        if (!existingEdgeSigs.has(sig)) {
          updatedEdges.push({ ...edge, isNew: true });
          existingEdgeSigs.add(sig);
        } else {
          const idx = updatedEdges.findIndex(e => `${e.source}-${e.target}-${e.type}` === sig);
          if (idx !== -1) updatedEdges[idx].isNew = true;
        }
      });

      return { nodes: updatedNodes, edges: updatedEdges };
    });
  }, []);

  const clearGraphState = useCallback(() => {
    setGraph({ nodes: [], edges: [] });
  }, []);

  return { graph, addGraphData, clearGraphState };
}
