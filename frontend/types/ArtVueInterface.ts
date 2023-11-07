import {createApp} from 'vue'
import {ArtVueGlobals} from '@/types/ArtVueGlobals'

export type ArtVueInterface = ReturnType<typeof createApp> & ArtVueGlobals
