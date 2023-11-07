import {VueCons} from 'vue-facing-decorator'
import {ArtVueGlobals} from '@/types/ArtVueGlobals'

// For typing the class function used with the @Component decorator. If you need to coerce
// an object into the resulting type, you'll want to use ArtVueInterface instead.
export type ArtVueClassInterface = VueCons<ArtVueGlobals>
