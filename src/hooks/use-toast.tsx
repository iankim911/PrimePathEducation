"use client"

import { toast as sonnerToast } from "sonner"

interface ToastProps {
  title?: string
  description?: string
  variant?: "default" | "destructive"
}

export function useToast() {
  const toast = ({ title, description, variant }: ToastProps) => {
    const message = title || ""
    const desc = description || ""
    
    if (variant === "destructive") {
      sonnerToast.error(message, {
        description: desc,
      })
    } else {
      sonnerToast.success(message, {
        description: desc,
      })
    }
  }

  return { toast }
}