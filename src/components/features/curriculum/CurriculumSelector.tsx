"use client"

import { useState, useEffect } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import type { CurriculumTree, CurriculumNode } from '@/lib/services/curriculum'

interface CurriculumSelectorProps {
  value?: string | null
  onValueChange: (nodeId: string | null, pathName: string | null) => void
  placeholder?: string
  label?: string
  disabled?: boolean
  allowEmpty?: boolean
}

// Helper function to build tree structure from flat nodes
function buildTreeFromFlatNodes(flatNodes: any[]): any[] {
  const nodeMap = new Map<string, any>()
  
  // Initialize all nodes
  flatNodes.forEach(node => {
    nodeMap.set(node.id, { ...node, children: [] })
  })

  // Build parent-child relationships
  const rootNodes: any[] = []
  
  flatNodes.forEach(node => {
    const nodeWithRelations = nodeMap.get(node.id)!
    
    if (node.parent_id) {
      const parent = nodeMap.get(node.parent_id)
      if (parent) {
        nodeWithRelations.parent = parent
        parent.children = parent.children || []
        parent.children.push(nodeWithRelations)
      }
    } else {
      rootNodes.push(nodeWithRelations)
    }
  })

  return rootNodes
}

// Helper function to filter options to only show leaf nodes (actual class levels)
function filterToDeepestLevel(options: Array<{
  id: string
  name: string
  pathName: string
  levelDepth: number
}>): Array<{
  id: string
  name: string
  pathName: string
  levelDepth: number
}> {
  if (options.length === 0) return options

  // Find nodes that don't have children (leaf nodes)
  const nodeIds = new Set(options.map(opt => opt.id))
  const parentIds = new Set()
  
  // Identify parent nodes by looking for nodes that are prefixes of other nodes' paths
  options.forEach(option => {
    options.forEach(other => {
      if (other.pathName.startsWith(option.pathName + ' > ')) {
        parentIds.add(option.id)
      }
    })
  })
  
  // Return only nodes that are not parents (i.e., leaf nodes)
  return options.filter(opt => !parentIds.has(opt.id))
}

export function CurriculumSelector({ 
  value, 
  onValueChange, 
  placeholder = "Select curriculum level",
  label,
  disabled = false,
  allowEmpty = true
}: CurriculumSelectorProps) {
  const [tree, setTree] = useState<CurriculumTree | null>(null)
  const [loading, setLoading] = useState(true)
  const [flatOptions, setFlatOptions] = useState<Array<{
    id: string
    name: string
    pathName: string
    levelDepth: number
  }>>([])

  const fetchCurriculumTree = async () => {
    try {
      const response = await fetch('/api/curriculum/nodes')
      const data = await response.json()
      
      // Handle both tree format and fallback flat format
      if (data.tree && data.tree.nodes) {
        // Tree format response
        setTree(data.tree)
        const allOptions = flattenTreeForSelection(data.tree.nodes || [])
        // Filter to only show deepest level nodes for class assignment
        const deepestOptions = filterToDeepestLevel(allOptions)
        setFlatOptions(deepestOptions)
      } else if (data.nodes && data.nodes.length > 0) {
        // Fallback flat format - build tree structure manually
        // Just work with the flat nodes directly for selection
        setTree(null)
        const allOptions = data.nodes.map((node: any) => ({
          value: node.id,
          label: node.name,
          level: node.level || 1
        }))
        // Filter to only show deepest level nodes for class assignment
        const deepestOptions = filterToDeepestLevel(allOptions)
        setFlatOptions(deepestOptions)
      } else {
        // No curriculum data available
        console.log('No curriculum data available')
        setTree(null)
        setFlatOptions([])
      }
    } catch (error) {
      console.error('Error fetching curriculum tree:', error)
      // Set empty state on error
      setTree(null)
      setFlatOptions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCurriculumTree()
  }, [])

  // Recursively flatten the tree to create selection options
  const flattenTreeForSelection = (
    nodes: any[], 
    parentPath: string = '',
    result: any[] = []
  ): any[] => {
    for (const node of nodes) {
      const pathName = parentPath ? `${parentPath} > ${node.name}` : node.name
      
      result.push({
        id: node.id,
        name: node.name,
        pathName,
        levelDepth: node.level_depth
      })

      // Recursively add children
      if (node.children && node.children.length > 0) {
        flattenTreeForSelection(node.children, pathName, result)
      }
    }
    return result
  }

  const handleValueChange = (selectedValue: string) => {
    if (selectedValue === 'empty') {
      onValueChange(null, null)
      return
    }

    const selectedOption = flatOptions.find(option => option.id === selectedValue)
    if (selectedOption) {
      onValueChange(selectedOption.id, selectedOption.pathName)
    }
  }

  const getSelectedOptionName = (): string => {
    if (!value) return placeholder
    const option = flatOptions.find(opt => opt.id === value)
    return option?.pathName || placeholder
  }

  if (loading) {
    return (
      <div className="space-y-2">
        {label && <Label className="text-gray-900">{label}</Label>}
        <Select disabled>
          <SelectTrigger>
            <SelectValue placeholder="Loading curriculum..." />
          </SelectTrigger>
        </Select>
      </div>
    )
  }

  if (!tree || flatOptions.length === 0) {
    return (
      <div className="space-y-2">
        {label && <Label className="text-gray-900">{label}</Label>}
        <div className="text-sm text-gray-500 p-2 border rounded-md bg-gray-50">
          No curriculum structure configured. Set up your curriculum first.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {label && <Label className="text-gray-900">{label}</Label>}
      <Select value={value || 'empty'} onValueChange={handleValueChange} disabled={disabled}>
        <SelectTrigger>
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent className="bg-white max-h-60">
          {allowEmpty && (
            <SelectItem value="empty" className="text-gray-900 italic">
              None selected
            </SelectItem>
          )}
          {flatOptions.map((option) => (
            <SelectItem key={option.id} value={option.id} className="text-gray-900">
              <div className="flex items-center gap-2">
                <span>{option.pathName}</span>
                <Badge variant="outline" className="text-xs">
                  Depth {option.levelDepth}
                </Badge>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}