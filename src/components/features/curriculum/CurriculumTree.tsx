"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { PlusCircle, Folder, ChevronDown, ChevronRight, Edit, Trash2 } from 'lucide-react'
import type { CurriculumTree, CurriculumNodeWithRelations, CurriculumSettings } from '@/lib/services/curriculum'

interface CurriculumTreeComponentProps {
  settings: CurriculumSettings | null
  onRefresh?: () => void
}

// Helper function to build tree structure from flat nodes
function buildTreeFromFlatNodes(flatNodes: any[]): CurriculumNodeWithRelations[] {
  const nodeMap = new Map<string, CurriculumNodeWithRelations>()
  
  // Initialize all nodes
  flatNodes.forEach(node => {
    nodeMap.set(node.id, { ...node, children: [] })
  })

  // Build parent-child relationships
  const rootNodes: CurriculumNodeWithRelations[] = []
  
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

export function CurriculumTreeComponent({ settings, onRefresh }: CurriculumTreeComponentProps) {
  const [tree, setTree] = useState<CurriculumTree | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  const fetchTree = async () => {
    if (!settings) {
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/curriculum/nodes')
      if (!response.ok) {
        throw new Error('Failed to fetch curriculum tree')
      }
      
      const data = await response.json()
      
      // Handle both tree format and fallback flat format
      if (data.tree) {
        setTree(data.tree)
      } else if (data.nodes) {
        // Convert flat nodes to tree structure manually
        const treeData = {
          settings: settings,
          nodes: buildTreeFromFlatNodes(data.nodes)
        }
        setTree(treeData)
      } else {
        setTree(null)
      }
    } catch (error) {
      console.error('Error fetching curriculum tree:', error)
      toast({
        title: "Error",
        description: "Could not load curriculum tree",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTree()
  }, [settings])

  const toggleExpanded = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  const getLevelName = (depth: number): string => {
    if (!settings) {
      // Better default names when no settings
      switch (depth) {
        case 1: return 'Program'
        case 2: return 'Track' 
        case 3: return 'Level'
        case 4: return 'Section'
        default: return `Level ${depth}`
      }
    }
    
    // Use settings but replace problematic names with better UX
    switch (depth) {
      case 1: return settings.level_1_name === 'Category' ? 'Program' : settings.level_1_name
      case 2: return settings.level_2_name === 'Program' ? 'Track' : settings.level_2_name
      case 3: return settings.level_3_name
      case 4: return settings.level_4_name
      default: return `Level ${depth}`
    }
  }

  const renderNode = (node: CurriculumNodeWithRelations, depth: number = 0): React.ReactNode => {
    const isExpanded = expandedNodes.has(node.id)
    const hasChildren = node.children && node.children.length > 0
    
    return (
      <div key={node.id} className="select-none">
        <div 
          className="flex items-center gap-2 py-2 px-3 hover:bg-gray-50 rounded-lg"
          style={{ marginLeft: `${depth * 20}px` }}
        >
          {/* Expand/Collapse Button */}
          {hasChildren ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => toggleExpanded(node.id)}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          ) : (
            <div className="w-6" />
          )}

          {/* Folder Icon */}
          <Folder className="h-4 w-4 text-gray-500" />

          {/* Node Info */}
          <div className="flex-1 flex items-center gap-3">
            <span className="font-medium text-gray-900">{node.name}</span>
            {node.code && (
              <Badge variant="secondary" className="text-xs">
                {node.code}
              </Badge>
            )}
            <Badge variant="outline" className="text-xs">
              {getLevelName(node.level_depth)}
            </Badge>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1">
            <AddNodeDialog
              parentNode={node}
              settings={settings}
              onSuccess={fetchTree}
            />
            <EditNodeDialog
              node={node}
              onSuccess={fetchTree}
            />
            <DeleteNodeDialog
              node={node}
              onSuccess={fetchTree}
            />
          </div>
        </div>

        {/* Children */}
        {hasChildren && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  if (!settings) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-gray-900">Curriculum Structure</CardTitle>
          <CardDescription className="text-gray-600">
            Configure your curriculum settings first before managing the structure.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-gray-900">Curriculum Structure</CardTitle>
          <CardDescription className="text-gray-600">
            Loading curriculum tree...
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-gray-900">Curriculum Structure</CardTitle>
            <CardDescription className="text-gray-600">
              Manage your {settings.max_depth}-level curriculum hierarchy
            </CardDescription>
          </div>
          <AddNodeDialog
            parentNode={null}
            settings={settings}
            onSuccess={fetchTree}
          />
        </div>
      </CardHeader>
      <CardContent>
        {!tree || !tree.nodes || tree.nodes.length === 0 ? (
          <div className="text-center py-8">
            <Folder className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No curriculum structure yet
            </h3>
            <p className="text-gray-600 mb-4">
              Create your first {settings.level_1_name.toLowerCase()} to get started.
            </p>
            <AddNodeDialog
              parentNode={null}
              settings={settings}
              onSuccess={fetchTree}
            />
          </div>
        ) : (
          <div className="space-y-1">
            {tree.nodes.map(node => renderNode(node))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Add Node Dialog Component
interface AddNodeDialogProps {
  parentNode: CurriculumNodeWithRelations | null
  settings: CurriculumSettings | null
  onSuccess?: () => void
}

function AddNodeDialog({ parentNode, settings, onSuccess }: AddNodeDialogProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: ''
  })

  const levelDepth = parentNode ? parentNode.level_depth + 1 : 1
  const canAdd = !settings || levelDepth <= settings.max_depth

  if (!canAdd) return null

  const getLevelNameForDepth = (settings: CurriculumSettings | null, depth: number): string => {
    if (!settings) {
      // Better default names when no settings
      switch (depth) {
        case 1: return 'Program'
        case 2: return 'Track'
        case 3: return 'Level' 
        case 4: return 'Section'
        default: return `Level ${depth}`
      }
    }
    
    // Use settings but replace problematic names with better UX
    switch (depth) {
      case 1: return settings.level_1_name === 'Category' ? 'Program' : settings.level_1_name
      case 2: return settings.level_2_name === 'Program' ? 'Track' : settings.level_2_name
      case 3: return settings.level_3_name
      case 4: return settings.level_4_name
      default: return `Level ${depth}`
    }
  }

  const levelName = getLevelNameForDepth(settings, levelDepth)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: `${levelName} name is required`,
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const response = await fetch('/api/curriculum/nodes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          parent_id: parentNode?.id || null,
          level_depth: levelDepth,
          name: formData.name.trim(),
          code: formData.code.trim() || null,
          description: formData.description.trim() || null,
          sort_order: 0
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to add ${levelName.toLowerCase()}`)
      }

      toast({
        title: "Success!",
        description: `${levelName} added successfully`,
      })

      setFormData({ name: '', code: '', description: '' })
      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to add ${levelName.toLowerCase()}. Please try again.`,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }


  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          variant={parentNode ? "ghost" : "default"}
          size={parentNode ? "sm" : "default"}
          className={parentNode ? "h-8 w-8 p-0" : "bg-gray-900 hover:bg-gray-800 text-white"}
        >
          <PlusCircle className={`h-4 w-4 ${!parentNode ? "mr-2" : ""}`} />
          {!parentNode && `Add ${levelName}`}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] bg-white text-gray-900">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add {levelName}</DialogTitle>
            <DialogDescription>
              {parentNode 
                ? `Add a new ${levelName.toLowerCase()} under "${parentNode.name}"`
                : `Create a new ${levelName.toLowerCase()} at the root level`
              }
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right text-gray-900">
                Name*
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3 bg-white text-gray-900 border-gray-300"
                placeholder={`Enter ${levelName.toLowerCase()} name`}
                required
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="code" className="text-right text-gray-900">
                Code
              </Label>
              <Input
                id="code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="col-span-3 bg-white text-gray-900 border-gray-300"
                placeholder="Optional short code"
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right text-gray-900">
                Description
              </Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="col-span-3 bg-white text-gray-900 border-gray-300"
                placeholder="Optional description"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)} className="border-gray-300 text-gray-900 hover:bg-gray-50">
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="bg-gray-900 hover:bg-gray-800 text-white">
              {loading ? 'Adding...' : `Add ${levelName}`}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Edit Node Dialog Component
function EditNodeDialog({ node, onSuccess }: { 
  node: CurriculumNodeWithRelations, 
  onSuccess?: () => void 
}) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    name: node.name,
    code: node.code || '',
    description: node.description || ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Name is required",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`/api/curriculum/nodes/${node.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name.trim(),
          code: formData.code.trim() || null,
          description: formData.description.trim() || null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to update curriculum node')
      }

      toast({
        title: "Success!",
        description: "Curriculum node updated successfully",
      })

      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update curriculum node. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
          <Edit className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] bg-white text-gray-900">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Curriculum Node</DialogTitle>
            <DialogDescription>
              Update the details for "{node.name}"
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-name" className="text-right text-gray-900">
                Name*
              </Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3 bg-white text-gray-900 border-gray-300"
                placeholder="Enter name"
                required
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-code" className="text-right text-gray-900">
                Code
              </Label>
              <Input
                id="edit-code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="col-span-3 bg-white text-gray-900 border-gray-300"
                placeholder="Optional short code"
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-description" className="text-right text-gray-900">
                Description
              </Label>
              <Input
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="col-span-3 bg-white text-gray-900 border-gray-300"
                placeholder="Optional description"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)} className="border-gray-300 text-gray-900 hover:bg-gray-50">
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="bg-gray-900 hover:bg-gray-800 text-white">
              {loading ? 'Updating...' : 'Update'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Delete Node Dialog Component
function DeleteNodeDialog({ node, onSuccess }: { 
  node: CurriculumNodeWithRelations, 
  onSuccess?: () => void 
}) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleDelete = async () => {
    setLoading(true)

    try {
      const response = await fetch(`/api/curriculum/nodes/${node.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete curriculum node')
      }

      toast({
        title: "Success!",
        description: "Curriculum node deleted successfully",
      })

      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete curriculum node. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const hasChildren = node.children && node.children.length > 0

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-600 hover:text-red-700">
          <Trash2 className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] bg-white text-gray-900">
        <DialogHeader>
          <DialogTitle className="text-red-600">Delete Curriculum Node</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete "{node.name}"?
            {hasChildren && (
              <span className="block mt-2 font-medium text-red-600">
                Warning: This will also delete all sub-categories and levels under this node.
              </span>
            )}
            <span className="block mt-2 text-gray-600">
              This action cannot be undone.
            </span>
          </DialogDescription>
        </DialogHeader>
        
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => setOpen(false)} className="border-gray-300 text-gray-900 hover:bg-gray-50">
            Cancel
          </Button>
          <Button 
            type="button" 
            disabled={loading} 
            onClick={handleDelete}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            {loading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}