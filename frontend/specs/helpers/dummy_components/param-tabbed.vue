<template>
  <div></div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {paramHandleMap} from '@/lib/lib'

  @Component
export default class ParamTabbed extends Vue {
    @paramHandleMap('tabName')
    private tab!: string

    @paramHandleMap('subTabName', undefined, ['tab-one', 'tab-two'], 'tab-two')
    private subTab!: string

    @paramHandleMap('subTabName', undefined, ['tab-one', 'tab-two'])
    private subTab2!: string

    @paramHandleMap('tabName', ['subTabName'])
    private altTab!: string
}
</script>
