import {createApp} from 'vue'
import {ArtVueGlobals} from '@/types/ArtVueGlobals.ts'

export type ArtVueInterface = ReturnType<typeof createApp> & ArtVueGlobals
