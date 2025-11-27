import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export async function GET() {
  try {
    
    // Test query to check connection
    const { data, error } = await supabase
      .from('academies')
      .select('*');

    if (error) {
      return NextResponse.json({ 
        success: false, 
        error: error.message 
      }, { status: 500 });
    }

    return NextResponse.json({ 
      success: true, 
      message: 'Database connected!',
      academies: data 
    });
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: 'Connection failed' 
    }, { status: 500 });
  }
}