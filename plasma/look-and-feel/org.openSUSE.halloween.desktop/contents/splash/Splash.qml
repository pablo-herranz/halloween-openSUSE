/*
    SPDX-FileCopyrightText: 2014 Marco Martin <mart@kde.org>
    SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>

    SPDX-License-Identifier: GPL-2.0-or-later

    Derived from Breeze's splash (plasma-workspace v6.8.0). The chameleon sits
    above a row of five pumpkins that light up as Plasma starts.
*/

import QtQuick
import org.kde.kirigami as Kirigami

import "palette.js" as Palette

Rectangle {
    id: root
    color: Palette.night

    property int stage

    // Candle flicker shared by every lit pumpkin
    property real flicker: 1

    onStageChanged: {
        if (stage >= 2 && content.opacity === 0 && !introAnimation.running) {
            introAnimation.running = true;
        }
    }

    SequentialAnimation on flicker {
        // Respect the user's "no animations" setting
        running: Kirigami.Units.longDuration > 1
        loops: Animation.Infinite
        NumberAnimation { to: 0.78; duration: 140; easing.type: Easing.InOutSine }
        NumberAnimation { to: 0.96; duration: 230; easing.type: Easing.InOutSine }
        NumberAnimation { to: 0.85; duration: 120; easing.type: Easing.InOutSine }
        NumberAnimation { to: 1.0; duration: 310; easing.type: Easing.InOutSine }
        NumberAnimation { to: 0.9; duration: 180; easing.type: Easing.InOutSine }
        NumberAnimation { to: 1.0; duration: 260; easing.type: Easing.InOutSine }
    }

    Image {
        anchors.fill: parent
        source: "images/background.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        Image {
            id: hero
            readonly property real size: Kirigami.Units.gridUnit * 14

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -Kirigami.Units.gridUnit * 2
            width: size
            height: size
            source: "images/hero.png"
            sourceSize.width: size
            sourceSize.height: size
            asynchronous: true
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: hero.bottom
            anchors.topMargin: Kirigami.Units.gridUnit * 2
            spacing: Kirigami.Units.gridUnit

            Repeater {
                model: 5

                delegate: Item {
                    id: lantern

                    required property int index
                    readonly property bool lit: root.stage >= index + 1

                    width: Kirigami.Units.gridUnit * 3
                    height: width

                    Image {
                        anchors.centerIn: parent
                        width: parent.width * 2.2
                        height: width
                        source: "images/glow.png"
                        opacity: litImage.opacity * root.flicker
                        asynchronous: true
                    }
                    Image {
                        anchors.fill: parent
                        source: "images/pumpkin-unlit.png"
                        sourceSize.width: width
                        sourceSize.height: height
                        asynchronous: true
                    }
                    Image {
                        id: litImage
                        anchors.fill: parent
                        source: "images/pumpkin-lit.png"
                        sourceSize.width: width
                        sourceSize.height: height
                        asynchronous: true
                        opacity: lantern.lit ? 1 : 0

                        Behavior on opacity {
                            SequentialAnimation {
                                // Stages 1-3 arrive together, so light those pumpkins one by one
                                PauseAnimation { duration: lantern.index < 3 ? lantern.index * 220 : 0 }
                                NumberAnimation { duration: Kirigami.Units.longDuration * 2; easing.type: Easing.OutQuad }
                            }
                        }
                    }
                }
            }
        }
    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0
        to: 1
        duration: Kirigami.Units.veryLongDuration * 2
        easing.type: Easing.InOutQuad
    }
}
