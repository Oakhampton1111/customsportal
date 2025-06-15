import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FiChevronRight, FiChevronDown, FiFolder, FiFolderOpen, FiFileText } from 'react-icons/fi';
import type { TariffTreeNode } from '../../services/tariffApi';
import { tariffApi } from '../../services/tariffApi';

interface TariffTreeViewProps {
  onCodeSelect?: (hsCode: string, description: string) => void;
  initialExpandedSections?: number[];
  className?: string;
}

interface TreeNodeProps {
  node: TariffTreeNode;
  onCodeSelect?: (hsCode: string, description: string) => void;
  onToggle: (nodeId: number) => void;
  isExpanded: boolean;
  level: number;
}

const TreeNode: React.FC<TreeNodeProps> = ({ node, onCodeSelect, onToggle, isExpanded, level }) => {
  const hasChildren = node.has_children || (node.children && node.children.length > 0);
  const isLeaf = node.is_leaf || !hasChildren;

  const handleToggle = () => {
    if (hasChildren) {
      onToggle(node.id);
    }
  };

  const handleSelect = () => {
    if (onCodeSelect) {
      onCodeSelect(node.hs_code, node.description);
    }
  };

  const getIcon = () => {
    if (isLeaf) {
      return <FiFileText className="h-4 w-4 text-blue-500" />;
    }
    return isExpanded ? 
      <FiFolderOpen className="h-4 w-4 text-amber-500" /> : 
      <FiFolder className="h-4 w-4 text-amber-600" />;
  };

  const getChevron = () => {
    if (isLeaf) return null;
    return isExpanded ? 
      <FiChevronDown className="h-4 w-4 text-gray-500" /> : 
      <FiChevronRight className="h-4 w-4 text-gray-500" />;
  };

  return (
    <div className="select-none">
      <div 
        className={`
          flex items-center py-1 px-2 hover:bg-gray-50 cursor-pointer rounded
          ${level === 0 ? 'font-semibold' : ''}
          ${level === 1 ? 'font-medium' : ''}
          ${level >= 2 ? 'text-sm' : ''}
        `}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={handleSelect}
      >
        <div 
          className="flex items-center space-x-1 mr-2"
          onClick={(e) => {
            e.stopPropagation();
            handleToggle();
          }}
        >
          {getChevron()}
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">
              {node.hs_code}
            </span>
            <span className="truncate" title={node.description}>
              {node.description}
            </span>
          </div>
        </div>
      </div>

      {isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              onCodeSelect={onCodeSelect}
              onToggle={onToggle}
              isExpanded={child.expanded}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const TariffTreeView: React.FC<TariffTreeViewProps> = ({ 
  onCodeSelect, 
  initialExpandedSections = [],
  className = ''
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<number>>(
    new Set(initialExpandedSections)
  );
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set());
  const [selectedSection, setSelectedSection] = useState<number | null>(null);

  // Fetch all sections
  const { 
    data: sections, 
    isLoading: sectionsLoading, 
    error: sectionsError 
  } = useQuery({
    queryKey: ['tariff-sections'],
    queryFn: tariffApi.getSections,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch tree data for expanded sections
  const { 
    data: treeData, 
    isLoading: treeLoading, 
    error: treeError 
  } = useQuery({
    queryKey: ['tariff-tree', selectedSection],
    queryFn: () => selectedSection ? tariffApi.getTariffTree(selectedSection, 3) : null,
    enabled: selectedSection !== null,
    staleTime: 5 * 60 * 1000,
  });

  const toggleSection = (sectionId: number) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
        if (selectedSection === sectionId) {
          setSelectedSection(null);
        }
      } else {
        newSet.add(sectionId);
        setSelectedSection(sectionId);
      }
      return newSet;
    });
  };

  const toggleNode = (nodeId: number) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  const updateNodeExpansion = (nodes: TariffTreeNode[]): TariffTreeNode[] => {
    return nodes.map(node => ({
      ...node,
      expanded: expandedNodes.has(node.id),
      children: node.children ? updateNodeExpansion(node.children) : undefined
    }));
  };

  if (sectionsLoading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="animate-pulse space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-8 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (sectionsError) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="text-red-600 bg-red-50 p-3 rounded-lg">
          <h3 className="font-medium">Error loading tariff sections</h3>
          <p className="text-sm mt-1">{sectionsError.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border rounded-lg ${className}`}>
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Schedule 3 - Tariff Classification</h2>
        <p className="text-sm text-gray-600 mt-1">
          Browse the complete Australian Customs Tariff hierarchy
        </p>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {sections?.map((section) => (
          <div key={section.id} className="border-b border-gray-100 last:border-b-0">
            <div
              className="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
              onClick={() => toggleSection(section.id)}
            >
              <div className="flex items-center space-x-2 mr-3">
                {expandedSections.has(section.id) ? 
                  <FiChevronDown className="h-5 w-5 text-gray-500" /> : 
                  <FiChevronRight className="h-5 w-5 text-gray-500" />
                }
                <FiFolder className="h-5 w-5 text-blue-600" />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3">
                  <span className="font-mono text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    Section {section.section_number}
                  </span>
                  <span className="font-medium text-gray-900 truncate">
                    {section.title}
                  </span>
                </div>
                {section.description && (
                  <p className="text-sm text-gray-600 mt-1 truncate" title={section.description}>
                    {section.description}
                  </p>
                )}
                {section.chapter_range && (
                  <p className="text-xs text-gray-500 mt-1">
                    Chapters: {section.chapter_range}
                  </p>
                )}
              </div>
            </div>

            {expandedSections.has(section.id) && (
              <div className="bg-gray-25 border-t">
                {selectedSection === section.id && treeLoading && (
                  <div className="p-4">
                    <div className="animate-pulse space-y-2">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="h-6 bg-gray-200 rounded ml-8"></div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedSection === section.id && treeError && (
                  <div className="p-4">
                    <div className="text-red-600 bg-red-50 p-3 rounded">
                      <p className="text-sm">Error loading section data: {treeError.message}</p>
                    </div>
                  </div>
                )}

                {selectedSection === section.id && treeData && (
                  <div className="py-2">
                    {updateNodeExpansion(treeData.nodes).map((node) => (
                      <TreeNode
                        key={node.id}
                        node={node}
                        onCodeSelect={onCodeSelect}
                        onToggle={toggleNode}
                        isExpanded={node.expanded}
                        level={0}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {sections && sections.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          <FiFolder className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No tariff sections available</p>
        </div>
      )}
    </div>
  );
};

export default TariffTreeView;
