import Vue, {CreateElement} from 'vue'
import {Prop} from 'vue-property-decorator'
import Component from 'vue-class-component'
import {NullClass} from '@/store/helpers/NullClass'
import deepEqual from 'fast-deep-equal'
import {Registry, AttrKeys} from '@/store/registry-base'

@Component
export class BaseController<S, D extends AttrKeys> extends Vue {
  @Prop({required: true})
  public initName!: string

  // Set this to false if the controller never fetches anything, and so should never be waited on to load.
  public isFetchableController = true

  @Prop({required: true})
  public schema!: S

  public name: string = ''

  // Replace this with the default module new instances should be installed under, like 'lists' or 'singles'.
  public baseModuleName = 'base'

  public baseClass: any = NullClass
  public registry!: Registry<D, BaseController<S, D>>

  // When migrating data, these keys will be excluded, expected to be handled by submodules.
  // For some reason, Array<keyof D> set as the type does not work as expected, and so we lose some type safety here.
  public submoduleKeys: string[] = []

  public purge(path?: string[]) {
    path = path || this.path
    if (this.state === undefined) {
      // Already purged.
      return
    }
    for (const key of this.submoduleKeys) {
      (this as any)[key].abandon((this as any)._uid)
    }
    this.kill()
    this.$store.unregisterModule(path)
  }

  public kill() {
    // Kills any AJAX request this module is making.
    this.commit('kill')
  }

  public register(path?: string[]) {
    let data: Partial<D> = {}
    path = path || this.path
    if (this.state) {
      if (deepEqual(path, this.path) || this.stateFor(path)) {
        // Already registered. Don't attempt to recreate the target module.
        return
      }
      data = {...this.state}
    }
    for (const key of this.submoduleKeys) {
      delete data[key as keyof D]
    }
    try {
      this.$store.registerModule(
        // eslint-disable-next-line new-cap
        path, new this.baseClass({...this.schema, ...data, ...{name: path.join('/')}}),
      )
    } catch (err) {
      console.error(
        `Failed registering ${JSON.stringify(path)}.` +
        'Likely, the parent path is not registered, but check error for more detail. It could also be an error ' +
        'in a watcher/computed property.',
      )
      throw err
    }
  }

  public abandon(uid: number) {
    this.registry.unhook(uid, this)
  }

  public migrate(name: string) {
    if (deepEqual(this.derivePath(name), this.path)) {
      // We're already here. Might mean that another parent module that referenced this one was updated.
      return
    }
    const oldState = this.state
    const oldName = this.name
    this.register(this.derivePath(name))
    this.name = name
    for (const key of this.submoduleKeys) {
      (this as any)[key].migrate(this.prefix + key)
    }
    this.registry.rename(oldName, name)
    this.$store.unregisterModule(this.derivePath(oldName))
  }

  public derivePath(name: string) {
    const path = name.split('/')
    if (path.length === 1) {
      path.unshift(this.baseModuleName)
    }
    return path
  }

  public get path() {
    return this.derivePath(this.name)
  }

  public stateFor(path: string[]) {
    let state = this.$store.state
    for (const namespace of path) {
      if (state === undefined) {
        return undefined
      }
      state = state[namespace]
    }
    return state
  }

  public get state() {
    return this.stateFor(this.path)
  }

  public attr(attrName: keyof D) {
    return this.state && this.state[attrName]
  }

  public get prefix() {
    return this.path.join('/') + '/'
  }

  public get purged() {
    return this.state === undefined
  }

  public getter(getterName: string) {
    return this.$store.getters[`${this.prefix}${getterName}`]
  }

  public commit(mutationName: string, payload?: any) {
    this.$store.commit(`${this.prefix}${mutationName}`, payload)
  }

  public dispatch(actionName: string, payload?: any) {
    return this.$store.dispatch(`${this.prefix}${actionName}`, payload)
  }

  public created() {
    this.name = this.initName
  }

  // noinspection JSMethodCanBeStatic
  public render(createElement: CreateElement) {
    // Used in tests so we can mount directly.
    return createElement('div')
  }

  public toJSON() {
    // Used to prevent the pretty printing service from exhausting all memory.
    return {type: this.constructor.name, name: this.name, state: this.state}
  }
}
