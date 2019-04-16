declare module 'vue-fragment' {
  import Vue, {PluginObject} from 'vue'
  export const Plugin: PluginObject<any>
  export class Fragment extends Vue {}
}
