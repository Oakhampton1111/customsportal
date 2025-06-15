import React, { useState, useCallback } from 'react';
import { FiChevronRight, FiChevronDown, FiFolder, FiFile } from 'react-icons/fi';

export interface TreeNode {
  id: string;
  label: string;
  children?: TreeNode[];
  icon?: React.ReactNode;
  badge?: string | number;
  metadata?: Record<string, unknown>;
}

interface EnhancedTreeProps {
  data: TreeNode[];
  onNodeSelect?: (node: TreeNode) => void;
  onNodeExpand?: (node: TreeNode, isExpanded: boolean) => void;
  selectedNodeId?: string;
  expandedNodes?: Set<string>;
  className?: string;
  searchTerm?: string;
}

interface TreeItemProps {
  node: TreeNode;
  level: number;
  isExpanded: boolean;
  isSelected: boolean;
  onSelect: (node: TreeNode) => void;
  onToggle: (node: TreeNode) => void;
  searchTerm?: string;
  expandedNodes: Set<string>;
  selectedNodeId?: string;
}

const TreeItem: React.FC<TreeItemProps> = ({
  node,
  level,
  isExpanded,
  isSelected,
  onSelect,
  onToggle,
  searchTerm,
  expandedNodes,
  selectedNodeId
}) => {
  const hasChildren = node.children && node.children.length > 0;
  const paddingLeft = `${level * 1.5 + 1}rem`;

  const highlightText = (text: string, search?: string) => {
    if (!search) return text;
    
    const regex = new RegExp(`(${search})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} style={{
          backgroundColor: 'var(--color-warning-100)',
          color: 'var(--color-warning-700)',
          padding: '0.125rem 0.25rem',
          borderRadius: 'var(--radius-sm)'
        }}>
          {part}
        </mark>
      ) : part
    );
  };

  const getNodeIcon = () => {
    if (node.icon) return node.icon;
    if (hasChildren) {
      return <FiFolder size={16} />;
    }
    return <FiFile size={16} />;
  };

  return (
    <div className="tree-node">
      <div
        className={`tree-item ${isSelected ? 'tree-item--selected' : ''}`}
        style={{ paddingLeft }}
        onClick={() => onSelect(node)}
      >
        {hasChildren && (
          <button
            className="tree-item__toggle"
            onClick={(e) => {
              e.stopPropagation();
              onToggle(node);
            }}
            style={{
              background: 'none',
              border: 'none',
              padding: '0.25rem',
              marginRight: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              color: 'var(--color-gray-500)',
              transition: 'color var(--transition-fast)'
            }}
          >
            {isExpanded ? <FiChevronDown size={14} /> : <FiChevronRight size={14} />}
          </button>
        )}
        
        {!hasChildren && (
          <div style={{ width: '1.75rem', marginRight: '0.5rem' }} />
        )}

        <div className="tree-item__icon">
          {getNodeIcon()}
        </div>

        <span className="tree-item__text">
          {highlightText(node.label, searchTerm)}
        </span>

        {node.badge && (
          <span className="tree-item__badge">
            {node.badge}
          </span>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div className="tree-item__children">
          {node.children!.map((child) => (
            <TreeItem
              key={child.id}
              node={child}
              level={level + 1}
              isExpanded={expandedNodes.has(child.id)}
              isSelected={selectedNodeId === child.id}
              onSelect={onSelect}
              onToggle={onToggle}
              searchTerm={searchTerm}
              expandedNodes={expandedNodes}
              selectedNodeId={selectedNodeId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const EnhancedTree: React.FC<EnhancedTreeProps> = ({
  data,
  onNodeSelect,
  onNodeExpand,
  selectedNodeId,
  expandedNodes = new Set(),
  className = '',
  searchTerm
}) => {
  const [internalExpandedNodes, setInternalExpandedNodes] = useState<Set<string>>(expandedNodes);
  const [internalSelectedNode, setInternalSelectedNode] = useState<string | undefined>(selectedNodeId);

  const handleNodeSelect = useCallback((node: TreeNode) => {
    setInternalSelectedNode(node.id);
    onNodeSelect?.(node);
  }, [onNodeSelect]);

  const handleNodeToggle = useCallback((node: TreeNode) => {
    const newExpanded = new Set(internalExpandedNodes);
    const isCurrentlyExpanded = newExpanded.has(node.id);
    
    if (isCurrentlyExpanded) {
      newExpanded.delete(node.id);
    } else {
      newExpanded.add(node.id);
    }
    
    setInternalExpandedNodes(newExpanded);
    onNodeExpand?.(node, !isCurrentlyExpanded);
  }, [internalExpandedNodes, onNodeExpand]);

  const filterNodes = (nodes: TreeNode[], search: string): TreeNode[] => {
    if (!search) return nodes;
    
    return nodes.reduce<TreeNode[]>((filtered, node) => {
      const matchesSearch = node.label.toLowerCase().includes(search.toLowerCase());
      const filteredChildren = node.children ? filterNodes(node.children, search) : [];
      
      if (matchesSearch || filteredChildren.length > 0) {
        filtered.push({
          ...node,
          children: filteredChildren.length > 0 ? filteredChildren : node.children
        });
      }
      
      return filtered;
    }, []);
  };

  const filteredData = searchTerm ? filterNodes(data, searchTerm) : data;

  return (
    <div className={`tree-container ${className}`}>
      {filteredData.length === 0 ? (
        <div style={{
          padding: 'var(--space-8)',
          textAlign: 'center',
          color: 'var(--color-gray-500)',
          fontSize: 'var(--text-sm)'
        }}>
          {searchTerm ? 'No matching items found' : 'No data available'}
        </div>
      ) : (
        filteredData.map((node) => (
          <TreeItem
            key={node.id}
            node={node}
            level={0}
            isExpanded={internalExpandedNodes.has(node.id)}
            isSelected={internalSelectedNode === node.id}
            onSelect={handleNodeSelect}
            onToggle={handleNodeToggle}
            searchTerm={searchTerm}
            expandedNodes={internalExpandedNodes}
            selectedNodeId={internalSelectedNode}
          />
        ))
      )}
    </div>
  );
};

export default EnhancedTree;
