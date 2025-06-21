import { NextRequest, NextResponse } from 'next/server';
import { backendRequest } from '@/app/api/api';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const data = await backendRequest('/auth/standard/login', {
            method: 'POST',
            body: JSON.stringify(body),
        });
        
        return NextResponse.json(data);
    } catch (error) {
        console.error('Login API error:', error);
        return NextResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
        );
    }
}
